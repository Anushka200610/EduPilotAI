"""Tests for 18-Field Intervention Report and Serialization."""

import pytest
from tools.report_tools import (
    generate_structured_report,
    save_report_to_json,
    export_reports_to_dataframe,
)
from orchestration.graph import run_student_analysis


def test_18_field_report_structure():
    """Verify that generated report contains all 18 standard fields."""
    state = run_student_analysis("STU1001")
    report = state["final_report"]

    required_fields = [
        "report_id",
        "timestamp",
        "student_id",
        "academic_term",
        "analysis_objective",
        "execution_plan",
        "attendance_indicators",
        "assessment_indicators",
        "assignment_indicators",
        "identified_concerns",
        "supporting_evidence",
        "recommended_interventions",
        "responsible_academic_role",
        "suggested_review_period",
        "expected_measurable_outcome",
        "missing_data_and_limitations",
        "critic_validation_results",
        "final_status",
    ]

    assert len(required_fields) == 18
    for f in required_fields:
        assert f in report, f"Missing report field: {f}"

    assert report["final_status"] in ["VALIDATED", "NEEDS_REVIEW", "VALIDATION_FAILED"]


def test_report_json_and_dataframe_export(tmp_path):
    """Verify JSON export and tabular DataFrame conversion."""
    state1 = run_student_analysis("STU1001")
    state2 = run_student_analysis("STU1016")

    reports = [state1["final_report"], state2["final_report"]]

    # Test JSON save
    save_path = tmp_path / "test_report.json"
    saved = save_report_to_json(reports[0], save_path)
    assert saved.exists()

    # Test DataFrame export
    df = export_reports_to_dataframe(reports)
    assert len(df) == 2
    assert "student_id" in df.columns
    assert "final_status" in df.columns
    assert "overall_attendance_pct" in df.columns
