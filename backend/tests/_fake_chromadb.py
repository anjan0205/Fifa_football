"""A minimal in-memory fake of the ``chromadb`` API.

Only the small surface used by ``app.rag_pipeline`` is implemented. Installing
this into ``sys.modules`` lets the real RAG pipeline be imported and unit-tested
deterministically, without pulling in the heavy chromadb dependency or
downloading embedding models over the network.
"""
import sys
import types


class _Collection:
    def __init__(self, name, embedding_function=None):
        self.name = name
        self.embedding_function = embedding_function
        self._store = {}  # id -> (document, metadata)

    def add(self, documents, metadatas, ids):
        for doc, meta, _id in zip(documents, metadatas, ids):
            self._store[_id] = (doc, meta)

    def count(self):
        return len(self._store)

    def query(self, query_texts, n_results=3):
        items = list(self._store.values())[:n_results]
        docs = [d for d, _ in items]
        metas = [m for _, m in items]
        distances = [0.1 * i for i in range(len(items))]
        return {
            "documents": [docs],
            "metadatas": [metas],
            "distances": [distances],
        }


class PersistentClient:
    def __init__(self, path=None):
        self.path = path
        self._collections = {}

    def get_or_create_collection(self, name, embedding_function=None):
        if name not in self._collections:
            self._collections[name] = _Collection(name, embedding_function)
        return self._collections[name]


class _DefaultEmbeddingFunction:
    def __call__(self, texts):
        return [[0.0] for _ in texts]


class _OpenAIEmbeddingFunction:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key
        self.model_name = model_name

    def __call__(self, texts):
        return [[0.0] for _ in texts]


def install():
    """Register the fake ``chromadb`` package in ``sys.modules``."""
    chromadb = types.ModuleType("chromadb")
    chromadb.PersistentClient = PersistentClient

    utils = types.ModuleType("chromadb.utils")
    embedding_functions = types.ModuleType("chromadb.utils.embedding_functions")
    embedding_functions.DefaultEmbeddingFunction = _DefaultEmbeddingFunction
    embedding_functions.OpenAIEmbeddingFunction = _OpenAIEmbeddingFunction

    utils.embedding_functions = embedding_functions
    chromadb.utils = utils

    sys.modules["chromadb"] = chromadb
    sys.modules["chromadb.utils"] = utils
    sys.modules["chromadb.utils.embedding_functions"] = embedding_functions
