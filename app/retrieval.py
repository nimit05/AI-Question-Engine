from typing import List, Dict, Optional
from embeddings import EmbeddingsManager
from query_parser import QueryParser


class QuestionRetriever:
    
    def __init__(self, embeddings_manager: EmbeddingsManager, query_parser: QueryParser):

        self.em = embeddings_manager
        self.qp = query_parser
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """ Retrieve top-k questions for a query """
        # Parse query
        filters = self.qp.parse_query(query)
        
        #Filter questions
        filtered_questions = self._filter_questions(filters)
        
        # Step 3: Vector search on filtered results
        results = self._vector_search(query, filtered_questions, top_k)
        
        return results
    
    def _filter_questions(self, filters: Dict) -> List[Dict]:
 
        filtered = self.em.questions
        
        # Filter by subtopic if specified
        if filters.get("subtopic"):
            filtered = [
                q for q in filtered 
                if q["subtopic"] == filters["subtopic"]
            ]
        
        # Filter by difficulty if specified
        if filters.get("difficulty"):
            filtered = [
                q for q in filtered 
                if q["difficulty"] == filters["difficulty"]
            ]
        
        return filtered
    
    def _vector_search(self, query: str, questions: List[Dict], top_k: int) -> List[Dict]:
    
        if not questions:
            return []
        
        # Search using FAISS
        results = self.em.search(query, top_k=len(questions))
        
        # Filter results to only include filtered questions
        question_ids = {q["id"] for q in questions}
        filtered_results = [r for r in results if r["id"] in question_ids]
        
        # Return top-k
        return filtered_results[:top_k]
    
    def get_questions_only(self, query: str, top_k: int = 5) -> List[str]:
 
        results = self.retrieve(query, top_k)
        return [r["question"] for r in results]

    # Test retriever
    from parser import load_questions_json
    from pathlib import Path
    
    data_dir = Path(__file__).parent.parent / "data"
    
    # Load embeddings
    em = EmbeddingsManager()
    em.load_index(
        str(data_dir / "faiss_index"),
        str(data_dir / "questions_metadata.json")
    )
    
    # Create retriever
    qp = QueryParser(use_openai=False)
    retriever = QuestionRetriever(em, qp)
    
    # Test queries
    test_queries = [
        "tough recursion questions",
        "easy array problems",
        "hard graph questions"
    ]
    
    print("Testing Retriever:\n")
    for test_query in test_queries:
        print(f"Query: {test_query}")
        results = retriever.retrieve(test_query, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['question']} ({r['subtopic']}, {r['difficulty']})")
        print()
