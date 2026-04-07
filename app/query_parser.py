import json
import os
from typing import Dict
import re


class QueryParser:
    
    DIFFICULTY_KEYWORDS = {
        "easy": ["easy", "simple", "beginner", "basic"],
        "hard": ["tough", "difficult", "hard", "challenging", "advanced"],
    }
    
    SUBTOPIC_KEYWORDS = {
        "Array": ["array", "arrays"],
        "Recursion": ["recursion", "recursive"],
        "Backtracking": ["backtracking", "backtrack"],
        "Graph": ["graph", "graphs"],
        "Dynamic Programming": ["dynamic", "dp", "programming"],
        "String": ["string", "strings"],
    }
    
    def __init__(self, use_openai: bool = False):

        self.use_openai = use_openai
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def parse_query(self, query: str) -> Dict:

        """returns Dictionary with subtopic and difficulty"""

        if self.use_openai and self.api_key:
            return self._parse_with_openai(query)
        else:
            return self._parse_with_rules(query)
    
    def _parse_with_rules(self, query: str) -> Dict:
        """Parse query using keyword matching rules (MVP approach)"""
        query_lower = query.lower()
        
        # Extract difficulty
        difficulty = "Medium"  # default
        for level, keywords in self.DIFFICULTY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                difficulty = level.capitalize()
                break
        
        # Extract subtopic
        subtopic = None
        for topic, keywords in self.SUBTOPIC_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                subtopic = topic
                break
        
        return {
            "subtopic": subtopic,
            "difficulty": difficulty
        }
    
    def _parse_with_openai(self, query: str) -> Dict:

        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""Parse this question query and extract the subtopic and difficulty level.

Query: "{query}"

Respond in JSON format:
{{
    "subtopic": "Array|Recursion|Backtracking|Graph|Dynamic Programming|String|null",
    "difficulty": "Easy|Medium|Hard"
}}

Rules:
- If difficulty keyword (easy/hard/tough) present, use it. Otherwise default to Medium.
- If subtopic keyword present, extract it. Otherwise null.
- Topic should be from the predefined list above.
- Always respond with valid JSON only.
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            print(f"OpenAI parsing failed: {e}. Falling back to rule-based parsing.")
            return self._parse_with_rules(query)

