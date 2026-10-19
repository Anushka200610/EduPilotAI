"""Tools package initialization."""

from tools.academic_tools import (
    get_student_profile,
    get_attendance_history,
    get_assessment_results,
    get_assignment_status,
    calculate_attendance,
    calculate_academic_indicators,
    validate_intervention_plan,
)
from tools.decision_rules import DecisionRulesEngine
from tools.report_tools import generate_structured_report, save_report_to_json, export_reports_to_dataframe

__all__ = [
    "get_student_profile",
    "get_attendance_history",
    "get_assessment_results",
    "get_assignment_status",
    "calculate_attendance",
    "calculate_academic_indicators",
    "validate_intervention_plan",
    "DecisionRulesEngine",
    "generate_structured_report",
    "save_report_to_json",
    "export_reports_to_dataframe",
]
