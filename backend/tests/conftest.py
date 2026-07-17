"""Shared pytest fixtures.

The backend engine is created at import time from ``DATABASE_URL`` and the RAG
pipeline instantiates a chromadb client at import time. Tests point the database
at an isolated SQLite database and install a lightweight fake ``chromadb`` so the
whole app (including the real ``rag_pipeline`` and ``ai_agents`` modules) can be
imported and exercised without external services or network access.
"""
import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Use SQLite instead of PostgreSQL and force the in-process MockLLM path by
# leaving the AI provider keys unset. These must be set before app modules are
# imported because the engine/settings are built at import time.
os.environ["DATABASE_URL"] = f"sqlite:///{BACKEND_ROOT / 'tests' / '_import_time.db'}"
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)

import types  # noqa: E402

from tests import _fake_chromadb  # noqa: E402

_fake_chromadb.install()


def _install_llm_provider_stubs():
    """Stub the chat-provider imports used only by ``ai_agents.get_llm``.

    With no API keys configured, ``get_llm`` returns the in-process MockLLM and
    never instantiates these classes, so lightweight stand-ins are enough. This
    avoids installing ``langchain-openai`` / ``langchain-google-genai`` (and the
    ``google-genai`` -> httpx>=0.28 pin that conflicts with the TestClient).
    """
    for mod_name, cls_name in (
        ("langchain_openai", "ChatOpenAI"),
        ("langchain_google_genai", "ChatGoogleGenerativeAI"),
    ):
        if mod_name not in sys.modules:
            module = types.ModuleType(mod_name)
            setattr(module, cls_name, type(cls_name, (), {}))
            sys.modules[mod_name] = module


_install_llm_provider_stubs()


@pytest.fixture()
def client():
    """A TestClient backed by a fresh, shared in-memory SQLite schema."""
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app import database, main, models

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    models.Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()
    models.Base.metadata.drop_all(bind=engine)
    engine.dispose()
