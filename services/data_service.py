"""Data Service for EduPilot AI.

Provides standard querying, loading, and schema validation for the
synthetic academic datasets (students, attendance, assessments, assignments).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from config.settings import settings


class DataService:
    """Service to load, cache, query, and validate academic data records."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.students_file.parent
        self.students_file = self.data_dir / "students.csv"
        self.attendance_file = self.data_dir / "attendance.csv"
        self.assessments_file = self.data_dir / "assessments.csv"
        self.assignments_file = self.data_dir / "assignments.csv"
        self.scenarios_file = self.data_dir / "scenarios_meta.json"

        # Cached DataFrames
        self._df_students: Optional[pd.DataFrame] = None
        self._df_attendance: Optional[pd.DataFrame] = None
        self._df_assessments: Optional[pd.DataFrame] = None
        self._df_assignments: Optional[pd.DataFrame] = None
        self._scenarios_meta: Optional[Dict[str, Any]] = None

    def refresh(self):
        """Force reload of cached datasets."""
        self._df_students = None
        self._df_attendance = None
        self._df_assessments = None
        self._df_assignments = None
        self._scenarios_meta = None

    @property
    def students(self) -> pd.DataFrame:
        if self._df_students is None:
            if not self.students_file.exists():
                raise FileNotFoundError(f"Missing {self.students_file}")
            self._df_students = pd.read_csv(self.students_file)
        return self._df_students

    @property
    def attendance(self) -> pd.DataFrame:
        if self._df_attendance is None:
            if not self.attendance_file.exists():
                raise FileNotFoundError(f"Missing {self.attendance_file}")
            self._df_attendance = pd.read_csv(self.attendance_file)
        return self._df_attendance

    @property
    def assessments(self) -> pd.DataFrame:
        if self._df_assessments is None:
            if not self.assessments_file.exists():
                raise FileNotFoundError(f"Missing {self.assessments_file}")
            self._df_assessments = pd.read_csv(self.assessments_file)
        return self._df_assessments

    @property
    def assignments(self) -> pd.DataFrame:
        if self._df_assignments is None:
            if not self.assignments_file.exists():
                raise FileNotFoundError(f"Missing {self.assignments_file}")
            self._df_assignments = pd.read_csv(self.assignments_file)
        return self._df_assignments

    @property
    def scenarios_meta(self) -> Dict[str, Any]:
        if self._scenarios_meta is None:
            if self.scenarios_file.exists():
                with open(self.scenarios_file, "r", encoding="utf-8") as f:
                    self._scenarios_meta = json.load(f)
            else:
                self._scenarios_meta = {}
        return self._scenarios_meta

    def student_exists(self, student_id: str) -> bool:
        """Check if student ID exists in the student directory."""
        if not student_id or not isinstance(student_id, str):
            return False
        clean_id = student_id.strip().upper()
        return clean_id in self.students["student_id"].values

    def get_all_student_ids(self) -> List[str]:
        """Return sorted list of all registered student IDs."""
        return sorted(self.students["student_id"].tolist())

    def get_student_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve demographic and registration details for a student."""
        clean_id = student_id.strip().upper()
        df = self.students
        match = df[df["student_id"] == clean_id]
        if match.empty:
            return None
        rec = match.iloc[0].to_dict()
        # Add scenario metadata if available
        meta = self.scenarios_meta.get(clean_id, {})
        rec["archetype"] = meta.get("archetype", "UNKNOWN")
        rec["archetype_description"] = meta.get("description", "")
        return rec

    def get_attendance_history(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieve subject-wise attendance logs for a student."""
        clean_id = student_id.strip().upper()
        df = self.attendance
        match = df[df["student_id"] == clean_id]
        if match.empty:
            return []
        return match.to_dict(orient="records")

    def get_assessment_results(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieve all assessment entries for a student."""
        clean_id = student_id.strip().upper()
        df = self.assessments
        match = df[df["student_id"] == clean_id]
        if match.empty:
            return []
        # Sort chronologically if assessment_date present
        if "assessment_date" in match.columns:
            match = match.sort_values(by=["subject_id", "assessment_date"])
        return match.to_dict(orient="records")

    def get_assignment_status(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieve all assignment submissions for a student."""
        clean_id = student_id.strip().upper()
        df = self.assignments
        match = df[df["student_id"] == clean_id]
        if match.empty:
            return []
        return match.to_dict(orient="records")

    def validate_dataset_schemas(self) -> Dict[str, Any]:
        """Comprehensive verification of datasets integrity and invariants."""
        errors = []

        # 1. Students validation
        req_student_cols = {"student_id", "program", "semester", "section", "academic_term"}
        if not req_student_cols.issubset(set(self.students.columns)):
            errors.append(f"students.csv missing columns: {req_student_cols - set(self.students.columns)}")

        # 2. Attendance validation
        req_att_cols = {"student_id", "subject_id", "classes_held", "classes_attended", "academic_term"}
        if not req_att_cols.issubset(set(self.attendance.columns)):
            errors.append(f"attendance.csv missing columns: {req_att_cols - set(self.attendance.columns)}")
        else:
            # Invariant: attended <= held
            invalid_att = self.attendance[self.attendance["classes_attended"] > self.attendance["classes_held"]]
            if not invalid_att.empty:
                errors.append(f"Found {len(invalid_att)} attendance records where attended > held")
            # Invariant: non-negative
            neg_att = self.attendance[
                (self.attendance["classes_attended"] < 0) | (self.attendance["classes_held"] < 0)
            ]
            if not neg_att.empty:
                errors.append(f"Found {len(neg_att)} attendance records with negative values")

        # 3. Assessments validation
        req_asm_cols = {"student_id", "subject_id", "assessment_name", "maximum_marks", "marks_obtained"}
        if not req_asm_cols.issubset(set(self.assessments.columns)):
            errors.append(f"assessments.csv missing columns: {req_asm_cols - set(self.assessments.columns)}")
        else:
            # Invariant: 0 <= marks_obtained <= maximum_marks
            invalid_marks = self.assessments[
                (self.assessments["marks_obtained"] > self.assessments["maximum_marks"]) |
                (self.assessments["marks_obtained"] < 0)
            ]
            if not invalid_marks.empty:
                errors.append(f"Found {len(invalid_marks)} assessment records with marks outside [0, max_marks]")

        # 4. Assignments validation
        req_asg_cols = {"student_id", "subject_id", "assignment_id", "submission_status"}
        if not req_asg_cols.issubset(set(self.assignments.columns)):
            errors.append(f"assignments.csv missing columns: {req_asg_cols - set(self.assignments.columns)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "students_count": len(self.students),
            "attendance_records": len(self.attendance),
            "assessment_records": len(self.assessments),
            "assignment_records": len(self.assignments),
        }


# Singleton service instance
data_service = DataService()
