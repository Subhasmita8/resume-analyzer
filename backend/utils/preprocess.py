"""
preprocess.py
-------------
Handles text cleaning and NLP preprocessing pipeline:
  - Lowercasing
  - Punctuation/special character removal
  - Stopword removal (NLTK)
  - Tokenization
  - Lemmatization (spaCy)
"""

import re
import nltk
import spacy

# ---------------------------------------------------------------------------
# One-time downloads (will be skipped if already present)
# ---------------------------------------------------------------------------
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

from nltk.corpus import stopwords

# Load spaCy English model (small pipeline; only tagger+lemmatizer needed)
try:
    _NLP = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. "
        "Run: python -m spacy download en_core_web_sm"
    )

_STOP_WORDS = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """
    Remove URLs, emails, special characters, and extra whitespace.

    Args:
        text: Raw input text.

    Returns:
        Lightly cleaned text (still has natural casing at this stage).
    """
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)
    # Remove non-alphabetic characters (keep spaces)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline: clean → lowercase → tokenize →
    stopword removal → lemmatize.

    Args:
        text: Raw resume or job-description text.

    Returns:
        Space-joined string of lemmatized, filtered tokens.
    """
    cleaned = clean_text(text)
    lowered = cleaned.lower()

    # spaCy pipeline for tokenization + lemmatization
    doc = _NLP(lowered)

    tokens = [
        token.lemma_
        for token in doc
        if (
            token.is_alpha                    # alphabetic only
            and not token.is_stop             # spaCy stop-word list
            and token.text not in _STOP_WORDS # NLTK stop-word list
            and len(token.text) > 1           # drop single-char noise
        )
    ]

    return " ".join(tokens)


def extract_keywords(text: str, top_n: int = 50) -> list[str]:
    """
    Return the top-N unique meaningful tokens from a text block.
    Used to build the keyword pool for the missing-skills comparison.

    Args:
        text: Raw text (resume or JD).
        top_n: Maximum number of keywords to return.

    Returns:
        List of unique keyword strings.
    """
    processed = preprocess(text)
    tokens = processed.split()
    # Preserve order but deduplicate
    seen: set[str] = set()
    unique_tokens: list[str] = []
    for tok in tokens:
        if tok not in seen:
            seen.add(tok)
            unique_tokens.append(tok)
    return unique_tokens[:top_n]
