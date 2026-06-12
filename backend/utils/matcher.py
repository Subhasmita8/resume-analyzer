"""
matcher.py
----------
Core matching engine:
  - TF-IDF vectorisation (scikit-learn)
  - Cosine similarity score
  - Missing keyword extraction
  - Actionable improvement suggestions
"""

from __future__ import annotations

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.preprocess import preprocess, extract_keywords


# ---------------------------------------------------------------------------
# Suggestion templates keyed by skill category patterns
# ---------------------------------------------------------------------------
_SKILL_SUGGESTIONS: list[tuple[list[str], str]] = [
    (
        ["docker", "kubernetes", "container", "helm", "k8s"],
        "Add containerisation experience (Docker, Kubernetes) — these are standard in modern deployments.",
    ),
    (
        ["aws", "azure", "gcp", "cloud", "lambda", "s3", "ec2"],
        "Include cloud platform exposure (AWS / Azure / GCP) with specific services used.",
    ),
    (
        ["sql", "database", "postgresql", "mysql", "mongodb", "nosql"],
        "Mention database skills with the specific engine and your query/schema design experience.",
    ),
    (
        ["machine learning", "ml", "deep learning", "neural", "tensorflow", "pytorch", "sklearn"],
        "Quantify ML work: model type, dataset size, and the metric improvement you achieved.",
    ),
    (
        ["api", "rest", "graphql", "fastapi", "flask", "django"],
        "Highlight any REST/GraphQL API design or consumption experience.",
    ),
    (
        ["git", "github", "gitlab", "version control", "ci", "cd", "pipeline"],
        "Show CI/CD and version-control practices — link to a GitHub profile or describe a pipeline you built.",
    ),
    (
        ["agile", "scrum", "jira", "sprint", "kanban"],
        "Call out Agile/Scrum participation: sprint reviews, stand-ups, story-pointing.",
    ),
    (
        ["communication", "presentation", "leadership", "teamwork", "collaboration"],
        "Add soft-skills evidence: cross-team projects, presentations given, or teams led.",
    ),
    (
        ["test", "unit test", "pytest", "jest", "tdd", "selenium"],
        "Mention testing practices (unit, integration, e2e) and any coverage targets you maintained.",
    ),
    (
        ["linux", "unix", "bash", "shell", "scripting"],
        "Include Linux/shell-scripting experience — it signals operational maturity.",
    ),
]

_GENERIC_SUGGESTIONS = [
    "Tailor your summary section to mirror the exact language in the job description.",
    "Quantify achievements with numbers (e.g., 'reduced load time by 40%', 'managed 5-person team').",
    "Ensure consistent formatting: font, bullet style, and date format throughout.",
    "Keep the resume to 1–2 pages; prioritise relevance over completeness.",
    "Add a skills section listing tools and technologies in a scannable format.",
]


def compute_match(resume_text: str, jd_text: str) -> dict:
    """
    Analyse how well a resume matches a job description.

    Args:
        resume_text: Raw resume text (before preprocessing).
        jd_text:     Raw job-description text (before preprocessing).

    Returns:
        dict with keys:
            score           (int)  – cosine similarity as 0-100 percentage
            missing_skills  (list) – keywords in JD absent from resume
            suggestions     (list) – actionable improvement tips
            matching_keywords (list) – keywords present in both
    """
    if not resume_text.strip():
        raise ValueError("Resume text is empty after extraction.")
    if not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    # --- 1. Preprocess ---
    resume_processed = preprocess(resume_text)
    jd_processed = preprocess(jd_text)

    # --- 2. TF-IDF vectorisation ---
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([resume_processed, jd_processed])

    # --- 3. Cosine similarity → percentage score ---
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    score = round(float(similarity) * 100, 1)

    # --- 4. Keyword gap analysis ---
    resume_keywords = set(extract_keywords(resume_text, top_n=200))
    jd_keywords = set(extract_keywords(jd_text, top_n=200))

    missing = sorted(jd_keywords - resume_keywords)
    matching = sorted(resume_keywords & jd_keywords)

    # Limit list sizes for clean UI output
    missing_skills = missing[:20]
    matching_keywords = matching[:30]

    # --- 5. Targeted suggestions ---
    suggestions = _build_suggestions(missing_skills, score)

    return {
        "score": score,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "matching_keywords": matching_keywords,
    }


def _build_suggestions(missing_skills: list[str], score: float) -> list[str]:
    """
    Generate targeted suggestions based on which skill categories are missing,
    then pad with generic advice if needed.

    Args:
        missing_skills: Keywords present in JD but absent from resume.
        score: Cosine similarity score (0-100).

    Returns:
        List of suggestion strings (max 6).
    """
    suggestions: list[str] = []
    missing_text = " ".join(missing_skills).lower()

    for keywords, suggestion in _SKILL_SUGGESTIONS:
        if any(kw in missing_text for kw in keywords):
            suggestions.append(suggestion)

    # Low score → add generic structural advice
    if score < 50:
        suggestions.append(
            "Your overall match is low — rewrite your bullet points to use keywords "
            "from the job description more directly."
        )

    # Pad to at least 3 suggestions with generic tips
    for tip in _GENERIC_SUGGESTIONS:
        if len(suggestions) >= 6:
            break
        if tip not in suggestions:
            suggestions.append(tip)

    return suggestions[:6]
