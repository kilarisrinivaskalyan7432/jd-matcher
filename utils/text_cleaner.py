import re

def clean_text(text: str) -> str:
    """
    Basic text cleaning:
    - lowercase
    - remove extra whitespace
    - keep letters, digits, spaces, and a few punctuation
    """
    if not text:
        return ""
    text = text.lower()
    # Keep letters, digits, spaces, . + - / #
    text = re.sub(r"[^a-z0-9\s.\+\-/#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text