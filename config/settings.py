"""EduPilot AI Configuration Module

Defines configurable thresholds, file paths, and runtime settings.
All settings are transparent, configurable, and backed by Pydantic.
"""

from pathlib import Path
from pydantic import BaseModel, Field


# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
REPORTS_DIR = BASE_DIR / "data" / "reports"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


class AcademicThresholds(BaseModel):
    """Configurable decision thresholds for academic intervention."""

    # Attendance threshold: percentage below which attendance concern is flagged
    min_attendance_pct: float = Field(
        default=75.0,
        ge=0.0,
        le=100.0,
        description="Minimum mandatory attendance percentage",
    )

    # Critical attendance threshold: below which high priority is assigned
    critical_attendance_pct: float = Field(
        default=65.0,
        ge=0.0,
        le=100.0,
        description="Critical attendance threshold requiring urgent intervention",
    )

    # Passing mark threshold: percentage below which performance concern is flagged
    min_passing_marks_pct: float = Field(
        default=40.0,
        ge=0.0,
        le=100.0,
        description="Minimum passing marks percentage",
    )

    # Critical marks threshold: below which high priority is assigned
    critical_marks_pct: float = Field(
        default=30.0,
        ge=0.0,
        le=100.0,
        description="Critical marks threshold requiring urgent intervention",
    )

    # Declining performance threshold: percentage-point decrease between comparable assessments
    decline_threshold_pct: float = Field(
        default=15.0,
        ge=0.0,
        le=100.0,
        description="Score drop in percentage points between consecutive assessments",
    )

    # Assignment concern threshold: number of missing/overdue assignments to trigger concern
    max_missing_assignments: int = Field(
        default=0,
        ge=0,
        description="Max permitted missing assignments before flagging",
    )


class AppSettings(BaseModel):
    """Global Application Settings"""

    app_name: str = "EduPilot AI"
    app_version: str = "1.0.0"
    academic_term: str = "Fall 2026"
    seed: int = 42

    # Bounded retries for Critic Agent
    max_critic_retries: int = 2

    # File paths
    students_file: Path = DATA_DIR / "students.csv"
    attendance_file: Path = DATA_DIR / "attendance.csv"
    assessments_file: Path = DATA_DIR / "assessments.csv"
    assignments_file: Path = DATA_DIR / "assignments.csv"
    scenarios_meta_file: Path = DATA_DIR / "scenarios_meta.json"

    # Active thresholds
    thresholds: AcademicThresholds = Field(default_factory=AcademicThresholds)


# Default singleton settings instance
settings = AppSettings()
