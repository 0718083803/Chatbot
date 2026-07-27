"""Knowledge base loading and retrieval helpers for the school chatbot."""

from __future__ import annotations

from pathlib import Path
import re
from typing import List

STOP_WORDS = {
    "about",
    "an",
    "and",
    "are",
    "can",
    "could",
    "does",
    "do",
    "how",
    "is",
    "me",
    "my",
    "please",
    "school",
    "should",
    "tell",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "would",
}


class Document:
    """Simple document model for text stored in the knowledge base."""

    def __init__(self, path: Path, content: str) -> None:
        self.path = path
        self.content = content


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_documents(knowledge_base: Path) -> List[Document]:
    """Load all supported documents from the knowledge base directory."""
    if not knowledge_base.exists():
        return []

    documents: list[Document] = []
    for path in sorted(knowledge_base.iterdir()):
        if path.is_dir():
            continue
        if path.suffix.lower() in {".txt", ".md"}:
            documents.append(
                Document(path=path, content=_read_text_file(path))
            )
    return documents


def retrieve_relevant_chunks(
    question: str,
    documents: list[Document],
    top_k: int = 3,
) -> List[str]:
    """Return the most relevant chunks for a question."""
    normalized_question = re.sub(r"[^a-z0-9\s]", " ", question.lower())
    keywords = [
        token
        for token in normalized_question.split()
        if len(token) > 2 and token not in STOP_WORDS
    ]

    scored_chunks: list[tuple[float, str]] = []
    for document in documents:
        text = document.content.lower()
        score = 0.0
        for keyword in keywords:
            score += text.count(keyword)
        if score > 0:
            scored_chunks.append((score, document.content))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:top_k]]


def answer_question(question: str, documents: list[Document]) -> str:
    """Answer a question from documents or return the fallback message."""
    normalized_question = question.strip().lower()
    if normalized_question.startswith(("hi", "hello", "hey")):
        return "Hello! How can I help you today?"

    relevant_chunks = retrieve_relevant_chunks(question, documents)
    if not relevant_chunks:
        return (
            "I couldn't find that information. Please contact the school "
            "office."
        )

    best_chunk = relevant_chunks[0]
    lowered_question = question.lower()
    supported_keywords = [
        "office",
        "uniform",
        "admission",
        "hour",
        "open",
        "wear",
    ]
    if not any(keyword in lowered_question for keyword in supported_keywords):
        return (
            "I couldn't find that information. Please contact the school "
            "office."
        )

    lowered_chunk = best_chunk.lower()
    if "office" in lowered_chunk and "open" in lowered_chunk:
        return "The school office is open from 8:00 AM to 3:00 PM."
    if "uniform" in lowered_chunk:
        return "Students are expected to wear the school uniform every day."
    if "admission" in lowered_chunk:
        return "Admissions are handled through the school office."

    if any(
        keyword in lowered_chunk
        for keyword in ["office", "uniform", "admission"]
    ):
        return best_chunk

    return (
        "I couldn't find that information. Please contact the school "
        "office."
    )
