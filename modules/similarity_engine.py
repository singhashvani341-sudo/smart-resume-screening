"""Calculate NLP similarity between job descriptions and resumes."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.text_processor import prepare_for_similarity


def calculate_similarity(
    job_description: str,
    resume_text: str,
) -> float:
    """Calculate TF-IDF cosine similarity on a 0 to 100 scale."""

    if not job_description or not resume_text:
        return 0.0

    processed_job_description = prepare_for_similarity(job_description)
    processed_resume_text = prepare_for_similarity(resume_text)

    if not processed_job_description or not processed_resume_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer()

        tfidf_matrix = vectorizer.fit_transform(
            [
                processed_job_description,
                processed_resume_text,
            ]
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2],
        )[0][0]

        similarity_percentage = similarity * 100

        return round(
            max(0.0, min(100.0, similarity_percentage)),
            2,
        )

    except ValueError:
        return 0.0


def calculate_multiple_similarities(
    job_description: str,
    resume_texts: list[str],
) -> list[float]:
    """Calculate similarity scores for multiple resumes independently."""

    if not resume_texts:
        return []

    return [
        calculate_similarity(job_description, resume_text)
        for resume_text in resume_texts
    ]