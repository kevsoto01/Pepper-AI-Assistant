from __future__ import annotations

from typing import Any, Callable, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sentence_transformers import SentenceTransformer


class GeneralKnowledgeRAG:
    def __init__(
        self,
        collection_name: str = "general_knowledge",
        qdrant_path: str = "./pepper_v2_app/models/rag/qdrant_local",
        embedding_model_name: str = (
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
    ):
        self.collection_name = collection_name
        self.qdrant_path = qdrant_path
        self.embedding_model_name = embedding_model_name

        self.load()

    def load(self):

        print("Loading knowledge base...")
        self.client = QdrantClient(path=self.qdrant_path)
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        existing = {
            collection.name
            for collection in self.client.get_collections().collections
        }

        if self.collection_name not in existing:
            self.client.close()
            raise RuntimeError(
                f"Collection '{self.collection_name}' was not found "
                f"at '{self.qdrant_path}'. Run db_embedder.py first."
            )

    def close(self) -> None:
        self.client.close()

    def search(
        self,
        query: str,
        top_k: int = 5,
        language: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []

        query_vector = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            query_filter=self._build_filter(
                language=language,
                source_type=source_type,
            ),
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

    def build_context(
        self,
        question: str,
        results: list[dict[str, Any]],
    ) -> str:
        context_blocks = []

        for index, result in enumerate(results, start=1):
            context_blocks.append(
                # f"[Source {index}]\n"
                f"Title: {result.get('title')}\n"
                # f"URL: {result.get('url')}\n"
                f"Text:\n{result.get('text')}"
            )

        context = (
            "\n\n".join(context_blocks)
            if context_blocks
            else "No relevant context found."
        )

        return context

    def _build_filter(
        self,
        language: Optional[str],
        source_type: Optional[str],
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


def run_interactive_search() -> None:
    with GeneralKnowledgeRAG() as rag:
        while True:
            question = input(
                "Ask your question here: "
            ).strip()

            if not question:
                break

            results = rag.search(
                query=question,
                top_k=4,
            )

            # for index, result in enumerate(results, start=1):
            #     print("=" * 80)
            #     print(f"Result {index}")
            #     print("Title:", result["title"])
            #     print("Score:", result["score"])
            #     print("URL:", result["url"])
            #     print(result["text"][:700])
            context = rag.build_context(question, results)
            print(context)

if __name__ == "__main__":
    run_interactive_search()