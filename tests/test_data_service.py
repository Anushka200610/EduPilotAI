"""Tests for DataService and Dataset Schemas."""

import pytest
from services.data_service import data_service
from scripts.generate_data import generate_synthetic_data


def test_datasets_exist_and_non_empty():
    """Verify that all 4 synthetic CSV files exist and have data."""
    assert len(data_service.students) >= 100
    assert len(data_service.attendance) > 0
    assert len(data_service.assessments) > 0
    assert len(data_service.assignments) > 0


def test_schema_validation():
    """Verify schema integrity and mathematical invariants."""
    res = data_service.validate_dataset_schemas()
    assert res["valid"] is True
    assert len(res["errors"]) == 0
    assert res["students_count"] >= 100


def test_student_lookup():
    """Verify student profile retrieval and existence checks."""
    assert data_service.student_exists("STU1001") is True
    assert data_service.student_exists("STU9999") is False

    profile = data_service.get_student_profile("STU1001")
    assert profile is not None
    assert profile["student_id"] == "STU1001"
    assert profile["program"] in ["B.Tech AIML", "B.Tech CSE", "B.Tech Data Science"]
    assert profile["archetype"] == "STRONG_PERFORMANCE"


def test_attendance_records():
    """Verify attendance records invariants (attended <= held)."""
    records = data_service.get_attendance_history("STU1001")
    assert len(records) > 0
    for r in records:
        assert r["classes_attended"] <= r["classes_held"]
        assert r["classes_attended"] >= 0


def test_assessment_records():
    """Verify assessment marks bounds."""
    records = data_service.get_assessment_results("STU1001")
    assert len(records) > 0
    for r in records:
        assert 0.0 <= r["marks_obtained"] <= r["maximum_marks"]


def test_assignment_records():
    """Verify assignment records and valid statuses."""
    records = data_service.get_assignment_status("STU1001")
    assert len(records) > 0
    valid_statuses = {"SUBMITTED", "LATE", "MISSING", "PENDING"}
    for r in records:
        assert r["submission_status"] in valid_statuses
