import json
import csv
from pathlib import Path
from typing import List, Dict


def parse_markdown_dataset(file_path: str) -> List[Dict]:

    questions = []
    question_id = 1
    current_category = None
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Extract category
        if line.startswith("Category:"):
            current_category = line.replace("Category:", "").strip()
            continue
        
        # Extract questions (lines starting with *)
        if line.startswith("*"):
            question_text = line.replace("*", "").strip()
            
            question = {
                "id": f"q{question_id}",
                "question": question_text,
                "topic": "DSA",
                "subtopic": current_category,
                "difficulty": "Medium",
                "type": "Coding"
            }
            
            questions.append(question)
            question_id += 1
    
    return questions


def _normalize_difficulty(level: str) -> str:
    if not level:
        return "Medium"

    level_clean = level.strip().lower()
    mapping = {
        "basic": "Easy",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
    }
    return mapping.get(level_clean, "Medium")


def _infer_subtopic(question_text: str) -> str:
    text = question_text.lower()
    topic_keywords = {
        "Array": ["array", "subarray", "kadane", "prefix", "window"],
        "Recursion": ["recursion", "recursive", "tower of hanoi"],
        "Backtracking": ["backtracking", "n queen", "sudoku", "subset", "permutation"],
        "Graph": ["graph", "bfs", "dfs", "shortest path", "cycle", "tree", "topological"],
        "Dynamic Programming": ["dp", "dynamic", "knapsack", "lcs", "lis", "memo"],
        "String": ["string", "substring", "palindrome", "anagram", "pattern"],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in text for keyword in keywords):
            return topic

    return "Unknown"


def parse_csv_dataset(file_path: str) -> List[Dict]:

    questions: List[Dict] = []

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, start=1):
            question_text = (row.get("Question Name") or "").strip()
            if not question_text:
                continue

            difficulty = _normalize_difficulty(row.get("Difficulty Level", ""))
            subtopic = _infer_subtopic(question_text)

            question = {
                "id": f"q{idx}",
                "question": question_text,
                "topic": "DSA",
                "subtopic": subtopic,
                "difficulty": difficulty,
                "type": "Coding",
            }
            questions.append(question)

    return questions


def save_questions_json(questions: List[Dict], output_path: str) -> None:

    with open(output_path, 'w') as f:
        json.dump(questions, f, indent=2)
    
    print(f"✓ Saved {len(questions)} questions to {output_path}")


def load_questions_json(file_path: str) -> List[Dict]:
    """
    Load questions from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of question dictionaries
    """
    with open(file_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    # Parse CSV dataset and save to JSON
    csv_file = Path(__file__).parent.parent / "data" / "questionsDataset.csv"
    output_file = Path(__file__).parent.parent / "data" / "questions.json"

    questions = parse_csv_dataset(str(csv_file))
    save_questions_json(questions, str(output_file))

    print(f"Parsed dataset: {len(questions)} questions")
    print(f"Sample question: {questions[0]}")
