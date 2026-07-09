from __future__ import annotations

import hashlib
import re
import uuid
from typing import Any, Dict, List, Optional

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer


class GeneralKnowledgeRAG:
    def __init__(
        self,
        collection_name: str = "general_knowledge",
        qdrant_path: str = "./qdrant_local",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size_words: int = 120,
        chunk_overlap_words: int = 30,
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(path=qdrant_path)
        self.embedding_model = SentenceTransformer(embedding_model_name)

        self.chunk_size_words = chunk_size_words
        self.chunk_overlap_words = chunk_overlap_words

        test_vector = self.embedding_model.encode(["test"], normalize_embeddings=True)[0]
        self.vector_size = len(test_vector)

        self._ensure_collection()
    
    
    def close(self) -> None:
        self.client.close()

    def _ensure_collection(self) -> None:
        existing = [c.name for c in self.client.get_collections().collections]

        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def fetch_wikipedia_page(self, title: str, language: str = "en") -> Dict[str, Any]:
        """
        Fetch plain text from Wikipedia using the MediaWiki Action API.
        """

        endpoint = f"https://{language}.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info",
            "explaintext": True,
            "redirects": True,
            "inprop": "url",
            "titles": title,
        }

        headers = {
            "User-Agent": "GeneralKnowledgeRAG/1.0 (local development)"
        }

        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        pages = data["query"]["pages"]

        page = next(iter(pages.values()))

        if "missing" in page:
            raise ValueError(f"Wikipedia page not found: {title}")

        return {
            "title": page.get("title", title),
            "url": page.get("fullurl"),
            "text": page.get("extract", ""),
            "language": language,
            "pageid": page.get("pageid"),
        }

    def ingest_wikipedia_pages(self, titles: List[str], language: str = "en") -> None:
        for title in titles:
            page = self.fetch_wikipedia_page(title=title, language=language)
            self.ingest_text(
                text=page["text"],
                metadata={
                    "source_type": "wikipedia",
                    "title": page["title"],
                    "url": page["url"],
                    "language": page["language"],
                    "pageid": page["pageid"],
                },
            )

    def ingest_text(self, text: str, metadata: Dict[str, Any]) -> None:
        clean_text = self._clean_text(text)
        chunks = self._chunk_text(clean_text)

        if not chunks:
            return

        vectors = self.embedding_model.encode(
            chunks,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        points = []

        for index, chunk in enumerate(chunks):
            chunk_id = self._stable_chunk_id(metadata, index, chunk)

            payload = {
                **metadata,
                "chunk_index": index,
                "text": chunk,
            }

            points.append(
                PointStruct(
                    id=chunk_id,
                    vector=vectors[index].tolist(),
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        language: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_vector = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        qdrant_filter = self._build_filter(
            language=language,
            source_type=source_type,
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            query_filter=qdrant_filter,
            with_payload=True,
            limit=top_k,
        ).points

        return [
            {
                "score": result.score,
                "text": result.payload.get("text", ""),
                "title": result.payload.get("title"),
                "url": result.payload.get("url"),
                "metadata": result.payload,
            }
            for result in results
        ]

    def build_prompt(self, question: str, results: List[Dict[str, Any]]) -> str:
        context_blocks = []

        for i, result in enumerate(results, start=1):
            context_blocks.append(
                f"[Source {i}]\n"
                f"Title: {result.get('title')}\n"
                f"URL: {result.get('url')}\n"
                f"Text:\n{result.get('text')}"
            )

        context = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."

        return f"""
                You are a retrieval-augmented assistant.

                Rules:
                - Answer using only the context below.
                - If the context does not contain the answer, say you do not have enough information.
                - Cite sources like [Source 1], [Source 2].
                - Keep the answer clear and direct.

                Context:
                {context}

                Question:
                {question}

                Answer:
                """.strip()

    def ask(self, question: str, llm_fn, top_k: int = 5) -> Dict[str, Any]:
        results = self.search(question, top_k=top_k)
        prompt = self.build_prompt(question, results)
        answer = llm_fn(prompt)

        return {
            "answer": answer,
            "sources": results,
            "prompt": prompt,
        }

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()

        if not words:
            return []

        chunks = []
        step = self.chunk_size_words - self.chunk_overlap_words

        for start in range(0, len(words), step):
            end = start + self.chunk_size_words
            chunk = " ".join(words[start:end])

            if len(chunk.split()) >= 40:
                chunks.append(chunk)

        return chunks

    def _stable_chunk_id(self, metadata: Dict[str, Any], index: int, chunk: str) -> str:
        base = f"{metadata.get('source_type')}:{metadata.get('title')}:{index}:{chunk[:100]}"
        digest = hashlib.md5(base.encode("utf-8")).hexdigest()
        return str(uuid.UUID(digest))

    def _build_filter(
        self,
        language: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> Optional[Filter]:
        conditions = []

        if language:
            conditions.append(
                FieldCondition(
                    key="language",
                    match=MatchValue(value=language),
                )
            )

        if source_type:
            conditions.append(
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value=source_type),
                )
            )

        if not conditions:
            return None

        return Filter(must=conditions)
    

if __name__ == "__main__":
    import time
    starttime = time.time()
    block = 2

    rag = GeneralKnowledgeRAG()
    print("\n\nClass initialized in {}ms".format(str(int(1000*(time.time()-starttime)))))
    starttime = time.time()

    try:
        if block == 1:
            pages = [
                "Artificial intelligence",
                "Machine learning",
                "Natural language processing",
                "Python programming language",
                "Miami",
                "Dominican Republic",
                "United States",
                "Albert Einstein",
                "World War II",
                "Solar System",
            ]

            rag.ingest_wikipedia_pages(pages)
            print(f"Ingested {len(pages)} Wikipedia pages into Qdrant.")

        elif block == 2:
            questions = [
                "What is the capitol of Dominican Republic?",
                "Who won world war 2?",
                "How many planets are in our solar system?",
                "How many dwarf planets are in our solar system?",
                "When was Miami founded?",
                "When was artificial intelligence first conceptualized?",
                "Who invented python?",
                "Can you do object oriented programming in Python?",
                "Can you do OOP in python?"
            ]
            iteration = 0
            timespentarray = [""]*len(questions)
            for question in questions:
                iteration += 1
                print("\n\nQuestion {}: ".format(iteration), question, "\n")
                results = rag.search(question, top_k=8)
                for i, result in enumerate(results, start=1):
                    print("=" * 80)
                    print(f"Result {i}")
                    print("Title:", result["title"])
                    print("Score:", result["score"])
                    print("URL:", result["url"])
                    print(result["text"][:700])
                timespent = str(int(1000*(time.time()-starttime)))
                print("\nRetrieved in {}ms\n\n\n".format(timespent))
                starttime = time.time()
                timespentarray[iteration-1] = timespent
            print(timespentarray)
        
    finally:
        rag.close()

    