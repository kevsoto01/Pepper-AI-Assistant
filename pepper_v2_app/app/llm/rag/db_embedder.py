from __future__ import annotations

import argparse
import hashlib
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer


DEFAULT_COLLECTION_NAME = "general_knowledge"
DEFAULT_QDRANT_PATH = "./pepper_v2_app/models/rag/qdrant_local"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHUNK_SIZE_WORDS = 120
DEFAULT_CHUNK_OVERLAP_WORDS = 30

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
VITAL_LEVEL_3_PAGE = "Wikipedia:Vital articles/Level 3"

WIKIMEDIA_USER_AGENT = os.getenv(
    "WIKIMEDIA_USER_AGENT",
    "GeneralKnowledgeRAG/1.0 (contact: replace-with-your-email@example.com)",
)


def open_database(
    qdrant_path: str,
    embedding_model_name: str,
) -> tuple[QdrantClient, SentenceTransformer]:
    client = QdrantClient(path=qdrant_path)
    model = SentenceTransformer(embedding_model_name)
    return client, model


def ensure_collection(
    client: QdrantClient,
    model: SentenceTransformer,
    collection_name: str,
) -> None:
    existing = {
        collection.name
        for collection in client.get_collections().collections
    }

    if collection_name in existing:
        return

    test_vector = model.encode(
        ["test"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=len(test_vector),
            distance=Distance.COSINE,
        ),
    )


def fetch_wikipedia_page(
    title: str,
    language: str = "en",
    maximum_attempts: int = 8,
) -> dict[str, Any]:
    endpoint = f"https://{language}.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info",
        "explaintext": True,
        "redirects": True,
        "inprop": "url",
        "titles": title,
        "maxlag": 5,
    }

    headers = {"User-Agent": WIKIMEDIA_USER_AGENT}

    for attempt in range(maximum_attempts):
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=60,
        )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            try:
                wait_seconds = int(retry_after)
            except (TypeError, ValueError):
                wait_seconds = min(300, 15 * (2 ** attempt))

            print(
                f"Rate limited while fetching '{title}'. "
                f"Waiting {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)
            continue

        if response.status_code in {502, 503, 504}:
            wait_seconds = min(120, 5 * (2 ** attempt))
            print(
                f"Wikipedia temporarily unavailable. "
                f"Waiting {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()

        data = response.json()
        page = next(iter(data["query"]["pages"].values()))

        if "missing" in page:
            raise ValueError(f"Wikipedia page not found: {title}")

        return {
            "title": page.get("title", title),
            "url": page.get("fullurl"),
            "text": page.get("extract", ""),
            "language": language,
            "pageid": page.get("pageid"),
        }

    raise RuntimeError(
        f"Could not download '{title}' after "
        f"{maximum_attempts} attempts."
    )


def fetch_vital_level_3_titles() -> list[str]:
    response = requests.get(
        WIKIPEDIA_API,
        params={
            "action": "parse",
            "page": VITAL_LEVEL_3_PAGE,
            "prop": "links",
            "format": "json",
            "formatversion": 2,
            "redirects": True,
        },
        headers={"User-Agent": WIKIMEDIA_USER_AGENT},
        timeout=60,
    )
    response.raise_for_status()

    titles: list[str] = []
    seen: set[str] = set()

    for link in response.json()["parse"]["links"]:
        title = link.get("title")

        if link.get("ns") != 0:
            continue

        if not title or title in seen:
            continue

        seen.add(title)
        titles.append(title)

    if not 950 <= len(titles) <= 1050:
        raise RuntimeError(
            f"Expected about 1,000 Level 3 articles, "
            f"but found {len(titles)}."
        )

    return titles


def load_titles_from_txt(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Title file not found: {file_path}")

    titles: list[str] = []
    seen: set[str] = set()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        title = raw_line.strip()

        if not title or title.startswith("#") or title in seen:
            continue

        seen.add(title)
        titles.append(title)

    return titles


def save_titles(titles: Iterable[str], file_path: str) -> None:
    Path(file_path).write_text(
        "\n".join(titles),
        encoding="utf-8",
    )


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> list[str]:
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be greater than zero.")

    if chunk_overlap_words < 0:
        raise ValueError("chunk_overlap_words cannot be negative.")

    if chunk_overlap_words >= chunk_size_words:
        raise ValueError(
            "chunk_overlap_words must be smaller than chunk_size_words."
        )

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    step = chunk_size_words - chunk_overlap_words

    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + chunk_size_words])

        if len(chunk.split()) >= 40:
            chunks.append(chunk)

    return chunks


def stable_chunk_id(
    metadata: dict[str, Any],
    index: int,
    chunk: str,
) -> str:
    base = (
        f"{metadata.get('source_type')}:"
        f"{metadata.get('title')}:"
        f"{index}:"
        f"{chunk[:100]}"
    )
    digest = hashlib.md5(base.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest))


def wikipedia_page_exists(
    client: QdrantClient,
    collection_name: str,
    pageid: int,
) -> bool:
    result = client.count(
        collection_name=collection_name,
        count_filter=Filter(
            must=[
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value="wikipedia"),
                ),
                FieldCondition(
                    key="pageid",
                    match=MatchValue(value=pageid),
                ),
            ]
        ),
        exact=True,
    )

    return result.count > 0


def ingest_text(
    client: QdrantClient,
    model: SentenceTransformer,
    collection_name: str,
    text: str,
    metadata: dict[str, Any],
    chunk_size_words: int = DEFAULT_CHUNK_SIZE_WORDS,
    chunk_overlap_words: int = DEFAULT_CHUNK_OVERLAP_WORDS,
) -> int:
    chunks = chunk_text(
        clean_text(text),
        chunk_size_words=chunk_size_words,
        chunk_overlap_words=chunk_overlap_words,
    )

    if not chunks:
        return 0

    vectors = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    points = []

    for index, chunk in enumerate(chunks):
        payload = {
            **metadata,
            "chunk_index": index,
            "text": chunk,
        }

        points.append(
            PointStruct(
                id=stable_chunk_id(metadata, index, chunk),
                vector=vectors[index].tolist(),
                payload=payload,
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True,
    )

    return len(points)


def ingest_wikipedia_titles(
    titles: Iterable[str],
    client: QdrantClient,
    model: SentenceTransformer,
    collection_name: str,
    source_list: str,
    language: str = "en",
    request_delay_seconds: float = 1.0,
) -> dict[str, Any]:
    title_list = [title.strip() for title in titles if title.strip()]

    failed_titles: list[str] = []
    ingested_articles = 0
    skipped_articles = 0
    chunks_added = 0
    started = time.time()

    for article_number, requested_title in enumerate(title_list, start=1):
        if article_number > 1 and request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

        print(
            f"\n[{article_number}/{len(title_list)}] "
            f"Processing: {requested_title}"
        )

        try:
            page = fetch_wikipedia_page(
                title=requested_title,
                language=language,
            )
        except (requests.RequestException, ValueError, RuntimeError) as error:
            print(f"Failed: {error}")
            failed_titles.append(requested_title)
            continue

        pageid = page.get("pageid")

        if pageid is not None and wikipedia_page_exists(
            client=client,
            collection_name=collection_name,
            pageid=pageid,
        ):
            skipped_articles += 1
            print(
                f"Already stored, skipping: {page['title']} "
                f"(page ID {pageid})"
            )
            continue

        page_started = time.time()

        added = ingest_text(
            client=client,
            model=model,
            collection_name=collection_name,
            text=page["text"],
            metadata={
                "source_type": "wikipedia",
                "source_list": source_list,
                "title": page["title"],
                "url": page["url"],
                "language": page["language"],
                "pageid": pageid,
            },
        )

        ingested_articles += 1
        chunks_added += added

        print(
            f"Ingested: {page['title']} | "
            f"{added} chunks | "
            f"{time.time() - page_started:.2f} seconds"
        )

    return {
        "requested_articles": len(title_list),
        "ingested_articles": ingested_articles,
        "skipped_articles": skipped_articles,
        "failed_titles": failed_titles,
        "chunks_added": chunks_added,
        "elapsed_seconds": time.time() - started,
    }


def print_summary(summary: dict[str, Any]) -> None:
    print("\nIngestion complete.")
    print(f"Requested articles: {summary['requested_articles']}")
    print(f"New articles ingested: {summary['ingested_articles']}")
    print(f"Existing articles skipped: {summary['skipped_articles']}")
    print(f"Failed articles: {len(summary['failed_titles'])}")
    print(f"Chunks added: {summary['chunks_added']}")
    print(f"Total time: {summary['elapsed_seconds'] / 60:.2f} minutes")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or extend the general-knowledge Qdrant database."
    )

    parser.add_argument(
        "--qdrant-path",
        default=DEFAULT_QDRANT_PATH,
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION_NAME,
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_EMBEDDING_MODEL,
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=1.0,
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--vital3",
        action="store_true",
        help="Ingest Wikipedia Vital Articles Level 3.",
    )
    source_group.add_argument(
        "--titles-file",
        help="Ingest Wikipedia page titles from a text file.",
    )

    parser.add_argument(
        "--titles-output",
        default="vital_articles_level_3.txt",
    )
    parser.add_argument(
        "--failed-output",
        default="wikipedia_failed_titles.txt",
    )

    args = parser.parse_args()

    if "replace-with-your-email" in WIKIMEDIA_USER_AGENT:
        raise RuntimeError(
            "Set a real contact email in WIKIMEDIA_USER_AGENT "
            "before downloading from Wikipedia."
        )

    if args.vital3:
        titles = fetch_vital_level_3_titles()
        save_titles(titles, args.titles_output)
        source_list = "vital_articles_level_3"
        print(
            f"Found {len(titles)} titles. "
            f"Saved them to {args.titles_output}"
        )
    else:
        titles = load_titles_from_txt(args.titles_file)
        source_list = Path(args.titles_file).stem
        print(
            f"Loaded {len(titles)} titles "
            f"from {args.titles_file}"
        )

    client, model = open_database(
        qdrant_path=args.qdrant_path,
        embedding_model_name=args.model,
    )

    try:
        ensure_collection(
            client=client,
            model=model,
            collection_name=args.collection,
        )

        summary = ingest_wikipedia_titles(
            titles=titles,
            client=client,
            model=model,
            collection_name=args.collection,
            source_list=source_list,
            request_delay_seconds=args.request_delay,
        )

        if summary["failed_titles"]:
            save_titles(
                summary["failed_titles"],
                args.failed_output,
            )
            print(
                f"Failed titles saved to "
                f"{args.failed_output}"
            )

        print_summary(summary)

    finally:
        client.close()


if __name__ == "__main__":
    main()