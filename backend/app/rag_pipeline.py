import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from .database import settings

class RAGPipeline:
    def __init__(self):
        # Persistent storage folder for vectors
        self.persist_directory = "./chroma_db"
        self.collection_name = "stadium_guide"
        
        # Setup embedding function
        if settings.OPENAI_API_KEY:
            self.emb_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-3-small"
            )
        else:
            # Fallback to local default sentence-transformer embeddings or custom mock in case of missing keys
            self.emb_fn = embedding_functions.DefaultEmbeddingFunction()

        # Initialize chromadb client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.emb_fn
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Ingest text documents/chunks into the Chroma Vector DB.
        """
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False

    def query(self, search_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query vector store for context chunks.
        """
        try:
            results = self.collection.query(
                query_texts=[search_text],
                n_results=top_k
            )
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def initialize_seed_data(self):
        """
        Populate the vector store with initial standard operating procedures (SOPs).
        """
        # Check if already seeded
        if self.collection.count() > 0:
            return

        seed_docs = [
            # Stadium bag rule
            "Bag Policy: Only clear bags smaller than 12x6x12 inches are allowed inside MetLife Stadium. Small clutch bags (4.5x6.5 inches) do not need to be clear.",
            # Prohibited items
            "Prohibited Items: Weapons of any kind, lasers, professional cameras with detachable lenses longer than 6 inches, glass bottles, metal cans, banners larger than 3x5 feet, and air horns.",
            # Re-entry
            "Re-entry Policy: Re-entry is strictly prohibited. Once you exit MetLife Stadium gates, you cannot enter again using the same ticket barcodes.",
            # Medical locations
            "Medical Rooms & First Aid: Medical rooms are fully staffed and located near Section 109, Section 143, Section 216, and Section 302. In emergencies, flag a volunteer or operations staff.",
            # Evacuation instructions
            "Emergency Evacuation: Exit planning directs fans to use the closest stairwell. Elevators and escalators will be automatically shut down during fire alarms to prevent trapping.",
            # NJ Transit
            "NJ Transit Trains: Express service to Secaucus and Penn Station NYC departs from the Stadium Transit Station every 8-12 minutes starting in the 2nd half.",
            # Rideshare pick-up
            "Uber/Lyft Rideshare pick-up: Designated rideshare zone is located at Lot G, which is a 15-minute walk from Gate D (East Gate)."
        ]
        
        seed_metadatas = [
            {"source": "stadium_rules.pdf", "category": "rules"},
            {"source": "stadium_rules.pdf", "category": "rules"},
            {"source": "stadium_rules.pdf", "category": "rules"},
            {"source": "emergency_egress.doc", "category": "emergency"},
            {"source": "emergency_egress.doc", "category": "emergency"},
            {"source": "transit_schedule.xls", "category": "transport"},
            {"source": "transit_schedule.xls", "category": "transport"}
        ]
        
        seed_ids = [f"doc_chunk_{i}" for i in range(len(seed_docs))]
        
        self.add_documents(seed_docs, seed_metadatas, seed_ids)

# Instantiate global pipeline helper
rag_pipeline = RAGPipeline()
# Automatically run seeding
try:
    rag_pipeline.initialize_seed_data()
except Exception:
    # Ignore errors during startup build if environment locks DB path
    pass
