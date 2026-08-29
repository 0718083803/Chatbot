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

    # find relevant documents
    relevant_chunks = retrieve_relevant_chunks(question, documents)
    if not relevant_chunks:
        return (
            "I couldn't find that information. Please contact the school "
            "office."
        )

    best_chunk = relevant_chunks[0]

    # quick canned responses for common topics
    lowered_question = normalized_question
    canned = {
        "office": "The school office is open from 8:00 AM to 3:00 PM.",
        "office hours": "The school office is open from 8:00 AM to 3:00 PM.",
        "uniform": "Students are expected to wear the school uniform every day.",
        "admission": "Admissions are handled through the school office.",
        "admissions": "Admissions are handled through the school office.",
        "library": "The library is open from 8:30 AM to 4:00 PM on school days.",
        "lunch": "Lunch menus change daily; check the notice board for weekly menus.",
        "tuition": "Tuition invoices are sent at the start of each term; payments can be made online or at the finance office.",
        "contact": "Main Office: +1-555-151-0041; Email: office@school.edu",
        "phone": "Main Office: +1-555-151-0041",
        "email": "office@school.edu",
        "holidays": "The academic calendar and holiday schedule are published each year on the school's website.",
        "bell": "Classes typically begin at 8:30 AM and end at 3:00 PM. See the full bell schedule on the school site.",
        "enrollment": "Application and enrollment deadlines vary by grade — contact admissions for details.",
        "parent": "Parent-teacher conferences are held twice per year; sign-ups are via the parent portal.",
        "it": "For IT help contact itsupport@school.edu or call +1-555-151-0099.",
        "lost": "Lost items are held in the main office for 30 days.",
        "parking": "Staff and student parking require permits issued by the main office.",
        "visitor": "All visitors must check in at the main office and wear a visitor badge.",
        "immunization": "Students must provide up-to-date immunization records to the school nurse.",
        "homework": "Homework expectations vary by grade; teachers publish assignments via the classroom platform.",
        "attendance": "To report an absence call the attendance line or submit the absence form on the website.",
        "exam": "Midterm and final exam dates are posted each term; contact the guidance office for accommodations.",
        "special education": "Support services and IEPs are coordinated through the special education office.",
        "cafeteria": "Cafeteria accounts are managed online; parents can add funds via the lunch portal.",
        "nurse": "The school nurse is available during school hours for first aid and health concerns.",
        "grades": "Grades are posted in the parent/student portal; transcript requests go through the registrar.",
        "bully": "To report bullying contact the principal or use the anonymous reporting form on the website.",
        "weather": "Closure and delay announcements are posted on the website and sent via alerts.",
    }

    # check canned map first (match any key present in the question)
    for key, response in canned.items():
        if key in lowered_question:
            return response

    # if no canned answer, try to extract a focused section from the best chunk
    # return the paragraph that best matches the question keywords
    lowered_chunk = best_chunk.lower()
    # if the chunk already looks like a short, focused answer, return it
    if len(lowered_chunk) < 400 and "\n" not in best_chunk:
        return best_chunk

    # split into paragraphs and pick the one with most overlap
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", best_chunk) if p.strip()]
    if paragraphs:
        qtokens = set(re.sub(r"[^a-z0-9\s]", " ", lowered_question).split())
        best_para = paragraphs[0]
        best_score = 0
        for para in paragraphs:
            tokens = set(re.sub(r"[^a-z0-9\s]", " ", para.lower()).split())
            score = len(qtokens & tokens)
            if score > best_score:
                best_score = score
                best_para = para
        # if we found any overlap, return that paragraph
        if best_score > 0:
            return best_para

    # fallback: return a shortened excerpt of the best chunk
    excerpt = best_chunk.strip().split("\n")[0]
    if len(excerpt) > 800:
        excerpt = excerpt[:800].rsplit(" ", 1)[0] + "..."
    return excerpt
