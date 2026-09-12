from typing import List, Set
from .text_cleaner import clean_text

def load_skills_list(skills_path: str) -> List[str]:
    """Load skills from a text file (one skill per line)."""
    with open(skills_path, "r", encoding="utf-8") as f:
        skills = [line.strip().lower() for line in f if line.strip()]
    return skills

def extract_skills(text: str, skills_list: List[str]) -> Set[str]:
    """
    Extract skills present in the given text.
    Simple substring match after cleaning.
    """
    cleaned = clean_text(text)
    found_skills = set()
    for skill in skills_list:
        if skill in cleaned:
            found_skills.add(skill)
    return found_skills