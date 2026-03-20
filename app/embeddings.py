"""
Embeddings module to generate and store vector embeddings using sentence-transformers and FAISS
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import pickle

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    raise ImportError("Please install sentence-transformers and faiss-cpu")


class EmbeddingsManager:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
 
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.questions = []
        self.dimension = 384
    
    def generate_embeddings(self, questions: List[Dict]) -> np.ndarray:

        question_texts = [q["question"] for q in questions]
        embeddings = self.model.encode(question_texts, convert_to_numpy=True)
        self.questions = questions
        return embeddings
    
    def build_index(self, embeddings: np.ndarray) -> None:

        """here embeddings.shape[1] is the dimension of the embedding vectors (e.g., 384 for all-MiniLM-L6-v2)"""
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings.astype('float32'))
        print(f"✓ Built FAISS index with {self.index.ntotal} vectors")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
       
        # Generate embedding for query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return results with similarity scores
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            question = self.questions[idx].copy()
            question["similarity_score"] = float(1 / (1 + distance))  # Convert distance to similarity
            results.append(question)
        
        return results
    
    def save_index(self, index_path: str, metadata_path: str) -> None:
        """
        Save FAISS index and metadata to disk
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save questions metadata
        """
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
        
        faiss.write_index(self.index, index_path)
        
        # Save questions metadata
        with open(metadata_path, 'w') as f:
            json.dump(self.questions, f, indent=2)
        
        print(f"✓ Saved FAISS index to {index_path}")
        print(f"✓ Saved metadata to {metadata_path}")
    
    def load_index(self, index_path: str, metadata_path: str) -> None:
        """
        Load FAISS index and metadata from disk
        
        Args:
            index_path: Path to FAISS index
            metadata_path: Path to questions metadata
        """
        self.index = faiss.read_index(index_path)
        
        with open(metadata_path, 'r') as f:
            self.questions = json.load(f)
        
        print(f"✓ Loaded FAISS index from {index_path}")
        print(f"✓ Loaded {len(self.questions)} questions from {metadata_path}")


if __name__ == "__main__":
    # Test embeddings manager
    from parser import load_questions_json
    
    data_dir = Path(__file__).parent.parent / "data"
    questions_file = data_dir / "questions.json"
    
    # Load questions
    questions = load_questions_json(str(questions_file))
    
    # Create embeddings
    em = EmbeddingsManager()
    embeddings = em.generate_embeddings(questions)
    em.build_index(embeddings)
    
    # Save index
    em.save_index(
        str(data_dir / "faiss_index"),
        str(data_dir / "questions_metadata.json")
    )
    
    # Test search
    results = em.search("array problems", top_k=3)
    print("\nSearch results for 'array problems':")
    for r in results:
        print(f"  - {r['question']} (similarity: {r['similarity_score']:.3f})")
