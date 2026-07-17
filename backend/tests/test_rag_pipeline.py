"""Unit tests for the RAG pipeline.

A fake ``chromadb`` (installed in ``conftest``) backs these tests, so they run
without the real vector store or network access.
"""
from app import rag_pipeline as rag_module
from app.rag_pipeline import RAGPipeline


def test_module_level_pipeline_is_seeded():
    # The global instance runs initialize_seed_data() at import time.
    assert rag_module.rag_pipeline.collection.count() == 7


def test_add_documents_success():
    pipe = RAGPipeline()
    ok = pipe.add_documents(
        documents=["hello"],
        metadatas=[{"source": "unit"}],
        ids=["id-1"],
    )
    assert ok is True
    assert pipe.collection.count() >= 1


def test_add_documents_handles_errors(monkeypatch):
    pipe = RAGPipeline()

    def boom(*args, **kwargs):
        raise RuntimeError("write failed")

    monkeypatch.setattr(pipe.collection, "add", boom)
    ok = pipe.add_documents(["x"], [{"a": 1}], ["i"])
    assert ok is False


def test_query_returns_flattened_results():
    pipe = RAGPipeline()
    pipe.add_documents(
        documents=["doc-a", "doc-b"],
        metadatas=[{"n": 1}, {"n": 2}],
        ids=["a", "b"],
    )
    result = pipe.query("anything", top_k=2)
    assert set(result.keys()) == {"documents", "metadatas", "distances"}
    assert result["documents"] == ["doc-a", "doc-b"]
    assert result["metadatas"] == [{"n": 1}, {"n": 2}]
    assert len(result["distances"]) == 2


def test_query_handles_errors(monkeypatch):
    pipe = RAGPipeline()

    def boom(*args, **kwargs):
        raise RuntimeError("query failed")

    monkeypatch.setattr(pipe.collection, "query", boom)
    result = pipe.query("anything")
    assert result == {"documents": [], "metadatas": [], "distances": []}


def test_initialize_seed_data_is_idempotent():
    pipe = RAGPipeline()
    pipe.initialize_seed_data()
    assert pipe.collection.count() == 7
    # Running again should not duplicate the seed documents.
    pipe.initialize_seed_data()
    assert pipe.collection.count() == 7


def test_initialize_seed_data_skips_when_populated():
    pipe = RAGPipeline()
    pipe.add_documents(["existing"], [{"s": 1}], ["existing-id"])
    pipe.initialize_seed_data()
    # Because the collection was non-empty, seeding is skipped.
    assert pipe.collection.count() == 1
