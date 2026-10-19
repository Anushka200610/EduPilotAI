"""Tests for Deterministic Decision Rules."""

import pytest
from tools.decision_rules import DecisionRulesEngine
from config.settings import AcademicThresholds


@pytest.fixture
def engine():
    return DecisionRulesEngine(AcademicThresholds(
        min_attendance_pct=75.0,
        min_passing_marks_pct=40.0,
        decline_threshold_pct=15.0,
        max_missing_assignments=0,
    ))


def test_calculate_attendance_percentage():
    """Verify standard and boundary attendance calculations."""
    assert DecisionRulesEngine.calculate_attendance_percentage(30, 40) == 75.0
    assert DecisionRulesEngine.calculate_attendance_percentage(0, 40) == 0.0
    assert DecisionRulesEngine.calculate_attendance_percentage(40, 40) == 100.0
    assert DecisionRulesEngine.calculate_attendance_percentage(0, 0) == 0.0


def test_attendance_invariants():
    """Verify that invalid attendance values raise ValueError."""
    with pytest.raises(ValueError, match="cannot exceed"):
        DecisionRulesEngine.calculate_attendance_percentage(45, 40)

    with pytest.raises(ValueError, match="Negative"):
        DecisionRulesEngine.calculate_attendance_percentage(-5, 40)


def test_calculate_marks_percentage():
    """Verify marks percentage calculations and boundary checks."""
    assert DecisionRulesEngine.calculate_marks_percentage(35, 50) == 70.0
    assert DecisionRulesEngine.calculate_marks_percentage(0, 50) == 0.0
    assert DecisionRulesEngine.calculate_marks_percentage(50, 50) == 100.0


def test_marks_invariants():
    """Verify that marks out of range raise ValueError."""
    with pytest.raises(ValueError, match="within"):
        DecisionRulesEngine.calculate_marks_percentage(55, 50)

    with pytest.raises(ValueError, match="within"):
        DecisionRulesEngine.calculate_marks_percentage(-2, 50)

    with pytest.raises(ValueError, match="positive"):
        DecisionRulesEngine.calculate_marks_percentage(10, 0)


def test_evaluate_attendance_rule(engine):
    """Verify attendance threshold evaluation."""
    records = [
        {"subject_id": "CS201", "classes_held": 40, "classes_attended": 28},  # 70% -> Flagged
        {"subject_id": "CS202", "classes_held": 40, "classes_attended": 36},  # 90% -> Normal
    ]
    concerns, summary = engine.evaluate_attendance(records)
    assert len(concerns) == 1
    assert concerns[0]["concern_type"] == "ATTENDANCE_LOW"
    assert concerns[0]["subject_id"] == "CS201"
    assert summary["overall_pct"] == 80.0


def test_evaluate_assessment_decline_rule(engine):
    """Verify score decline detection between sequential tests."""
    records = [
        {"subject_id": "AI201", "assessment_name": "Quiz 1", "maximum_marks": 20, "marks_obtained": 18, "assessment_date": "2026-08-01"},  # 90%
        {"subject_id": "AI201", "assessment_name": "Mid-Term", "maximum_marks": 50, "marks_obtained": 30, "assessment_date": "2026-09-15"},  # 60% -> Delta 30%
    ]
    concerns, summary = engine.evaluate_assessments(records)
    # Check decline concern
    decline = [c for c in concerns if c["concern_type"] == "PERFORMANCE_DECLINE"]
    assert len(decline) == 1
    assert decline[0]["subject_id"] == "AI201"
    assert decline[0]["metric_value"] == 30.0


def test_evaluate_assignments_rule(engine):
    """Verify missing assignment count detection."""
    records = [
        {"subject_id": "CS201", "assignment_id": "A1", "submission_status": "SUBMITTED"},
        {"subject_id": "CS201", "assignment_id": "A2", "submission_status": "MISSING"},
    ]
    concerns, summary = engine.evaluate_assignments(records)
    assert len(concerns) == 1
    assert concerns[0]["concern_type"] == "ASSIGNMENT_INCOMPLETE"
    assert summary["missing"] == 1
