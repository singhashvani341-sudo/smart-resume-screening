"""Orchestrate screening, ranking, database storage, and logging."""



from config import DATABASE_PATH
from modules.database import (
    get_all_candidates,
    initialize_database,
    save_candidate,
)
from modules.logger import log_exception, setup_logger
from modules.ranking_engine import rank_candidates
from modules.screening_pipeline import screen_multiple_resumes


def process_resume_batch(
    resumes: list[tuple[str, bytes]],
    job_description: str,
    required_experience: float = 0,
    required_education: str = "",
    required_certifications: list[str] | None = None,
    database_path: str = DATABASE_PATH,
) -> dict[str, list[dict[str, object]]]:
    """Run the complete resume screening workflow."""

    logger = setup_logger()

    initialize_database(database_path)

    screening_result = screen_multiple_resumes(
        resumes=resumes,
        job_description=job_description,
        required_experience=required_experience,
        required_education=required_education,
        required_certifications=required_certifications,
    )

    saved_candidates = []
    failed_resumes = screening_result["failed_resumes"].copy()

    for candidate in screening_result["successful_candidates"]:
        try:
            save_candidate(
                candidate,
                database_path,
            )

            saved_candidates.append(candidate)

            logger.info(
                "Candidate processed successfully: %s",
                candidate["file_name"],
            )


        except Exception as error:
            failed_resumes.append(
                {
                    "file_name": candidate["file_name"],
                    "error": str(error),
                }
            )

            log_exception(
                logger,
                f"Failed to save candidate: "
                f"{candidate['file_name']}",
            )

    ranked_candidates = rank_candidates(saved_candidates)

    return {
        "ranked_candidates": ranked_candidates,
        "failed_resumes": failed_resumes,
    }


def get_saved_rankings(
    database_path: str = DATABASE_PATH,
) -> list[dict[str, object]]:
    """Return all stored candidates with current rank numbers."""

    initialize_database(database_path)

    candidates = get_all_candidates(database_path)

    return rank_candidates(candidates)
