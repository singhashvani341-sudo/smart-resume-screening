"""Shared configuration settings for the project."""

# Supported resume file extensions.
SUPPORTED_FILE_EXTENSIONS = {".pdf", ".docx"}

# Maximum allowed resume size: 10 MB.
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
# Final candidate scoring weights.
SCORING_WEIGHTS = {
    "similarity": 0.30,
    "skills": 0.30,
    "experience": 0.20,
    "education": 0.10,
    "certifications": 0.10,
}

# SQLite database location.
DATABASE_PATH = "database/resume_screening.db"

# Application logging settings.
LOG_FILE_PATH = "logs/app.log"
LOG_LEVEL = "INFO"