from pathlib import Path

from app.knowledge import answer_question
from app.knowledge import load_documents
from app.knowledge import retrieve_relevant_chunks


def test_load_documents_reads_text_files() -> None:
    documents = load_documents(Path("knowledge_base"))

    assert documents
    assert any("school" in doc.content.lower() for doc in documents)


def test_retrieve_relevant_chunks_returns_matches() -> None:
    documents = load_documents(Path("knowledge_base"))
    chunks = retrieve_relevant_chunks(
        "What time does the school office open?",
        documents,
        top_k=3,
    )

    assert chunks
    assert any("office" in chunk.lower() for chunk in chunks)


def test_answer_question_returns_fallback_when_not_found() -> None:
    documents = load_documents(Path("knowledge_base"))
    answer = answer_question("What is the school mascot?", documents)

    expected = (
        "I couldn't find that information. Please contact the school office."
    )
    assert answer == expected
