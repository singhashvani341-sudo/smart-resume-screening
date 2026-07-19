"""Run the complete resume screening pipeline."""

import hashlib

from modules.candidate_extractor import (
    calculate_certification_score,
    calculate_education_score,
    calculate_experience_score,
    extract_candidate_information,
    extract_all_certifications,
    extract_education,
    load_certification_keywords,
    load_education_keywords,
)
from modules.resume_parser import extract_resume_text
from modules.scoring_engine import calculate_final_score
from modules.similarity_engine import calculate_similarity
from modules.skill_extractor import (
    compare_skills,
    extract_skills,
    load_skills_database,
)


def screen_resume(
    file_name: str,
    file_content: bytes,
    job_description: str,
    required_experience: float = 0,
    required_education: str = "",
    required_certifications: list[str] | None = None,
) -> dict[str, object]:
    """Process one resume and return its complete screening result."""

    if not job_description or not job_description.strip():
        raise ValueError("The job description cannot be empty.")

    if required_certifications is None:
        required_certifications = []

    resume_text, success, error = extract_resume_text(
        file_name,
        file_content,
    )

    if not success:
        raise ValueError(error)

    candidate_information = extract_candidate_information(
        resume_text
    )

    skills_database = load_skills_database()
    education_keywords = load_education_keywords()
    certification_keywords = load_certification_keywords()

    required_skills = extract_skills(
        job_description,
        skills_database,
    )

    candidate_skills = extract_skills(
        resume_text,
        skills_database,
    )

    skill_comparison = compare_skills(
        required_skills,
        candidate_skills,
    )

    candidate_education = extract_education(
        resume_text,
        education_keywords,
    )

    candidate_certifications = extract_all_certifications(
        resume_text,
        certification_keywords,
    )
    

    similarity_score = calculate_similarity(
        job_description,
        resume_text,
    )

    skill_score = skill_comparison[
        "skill_match_percentage"
    ]

    experience_score = calculate_experience_score(
        required_experience,
        candidate_information["experience"],
    )

    education_score = calculate_education_score(
        required_education,
        candidate_education,
    )

    certification_score = calculate_certification_score(
        required_certifications,
        candidate_certifications,
    )

    final_score = calculate_final_score(
        similarity_score,
        skill_score,
        experience_score,
        education_score,
        certification_score,
    )

    file_hash = hashlib.sha256(file_content).hexdigest()

    return {
        "file_name": file_name,
        "file_hash": file_hash,
        "name": candidate_information["name"],
        "email": candidate_information["email"],
        "phone": candidate_information["phone"],
        "experience": candidate_information["experience"],
        "education": candidate_education,
        "certifications": candidate_certifications,
        "skills": candidate_skills,
        "matched_skills": skill_comparison["matched_skills"],
        "missing_skills": skill_comparison["missing_skills"],
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "certification_score": certification_score,
        "final_score": final_score,
    }
    
    
def screen_multiple_resumes(
    resumes: list[tuple[str, bytes]],
    job_description: str,
    required_experience: float = 0,
    required_education: str = "",
    required_certifications: list[str] | None = None,
) -> dict[str, list[dict[str, object]]]:
    """Screen multiple resumes while isolating individual failures."""

    successful_candidates = []
    failed_resumes = []

    if not resumes:
        return {
            "successful_candidates": [],
            "failed_resumes": [],
        }

    for file_name, file_content in resumes:
        try:
            candidate = screen_resume(
                file_name=file_name,
                file_content=file_content,
                job_description=job_description,
                required_experience=required_experience,
                required_education=required_education,
                required_certifications=required_certifications,
            )

            successful_candidates.append(candidate)

        except Exception as error:
            failed_resumes.append(
                {
                    "file_name": file_name,
                    "error": str(error),
                }
            )

    return {
        "successful_candidates": successful_candidates,
        "failed_resumes": failed_resumes,
    }