"""Academic Tools for EduPilot AI.

Implements the 7 core academic tools defined in the project specification:
1. get_student_profile(student_id)
2. get_attendance_history(student_id)
3. get_assessment_results(student_id)
4. get_assignment_status(student_id)
5. calculate_attendance(student_id)
6. calculate_academic_indicators(student_id)
7. validate_intervention_plan(student_id, intervention_plan, indicators)

Used directly by agents and exposed standardly through the MCP server.
"""

from typing import Any, Dict, List, Optional
from services.data_service import data_service
from tools.decision_rules import DecisionRulesEngine
from config.settings import AcademicThresholds, settings


def get_student_profile(student_id: str) -> Dict[str, Any]:
    """Retrieve demographic and registration details for a student."""
    profile = data_service.get_student_profile(student_id)
    if profile is None:
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found in registry.",
            "student_id": student_id,
        }
    return {"success": True, "student_id": student_id, "data": profile}


def get_attendance_history(student_id: str) -> Dict[str, Any]:
    """Retrieve subject-wise attendance logs for a student."""
    if not data_service.student_exists(student_id):
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found.",
            "student_id": student_id,
            "records": [],
        }
    records = data_service.get_attendance_history(student_id)
    return {
        "success": True,
        "student_id": student_id,
        "count": len(records),
        "records": records,
    }


def get_assessment_results(student_id: str) -> Dict[str, Any]:
    """Retrieve all assessment entries for a student."""
    if not data_service.student_exists(student_id):
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found.",
            "student_id": student_id,
            "records": [],
        }
    records = data_service.get_assessment_results(student_id)
    return {
        "success": True,
        "student_id": student_id,
        "count": len(records),
        "records": records,
    }


def get_assignment_status(student_id: str) -> Dict[str, Any]:
    """Retrieve all assignment submission records for a student."""
    if not data_service.student_exists(student_id):
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found.",
            "student_id": student_id,
            "records": [],
        }
    records = data_service.get_assignment_status(student_id)
    return {
        "success": True,
        "student_id": student_id,
        "count": len(records),
        "records": records,
    }


def calculate_attendance(
    student_id: str, thresholds: Optional[AcademicThresholds] = None
) -> Dict[str, Any]:
    """Calculate attendance metrics and identify low attendance concerns."""
    if not data_service.student_exists(student_id):
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found.",
            "student_id": student_id,
        }

    records = data_service.get_attendance_history(student_id)
    engine = DecisionRulesEngine(thresholds)
    concerns, summary = engine.evaluate_attendance(records)

    return {
        "success": True,
        "student_id": student_id,
        "overall_attendance_pct": summary["overall_pct"],
        "total_attended": summary["total_attended"],
        "total_held": summary["total_held"],
        "subject_breakdown": summary["subjects"],
        "attendance_concerns": concerns,
    }


def calculate_academic_indicators(
    student_id: str, thresholds: Optional[AcademicThresholds] = None
) -> Dict[str, Any]:
    """Comprehensive calculation of attendance, assessments, assignments, and composite concerns."""
    if not data_service.student_exists(student_id):
        return {
            "success": False,
            "error": f"Student ID '{student_id}' not found.",
            "student_id": student_id,
        }

    profile = data_service.get_student_profile(student_id)
    att_records = data_service.get_attendance_history(student_id)
    asm_records = data_service.get_assessment_results(student_id)
    asg_records = data_service.get_assignment_status(student_id)

    engine = DecisionRulesEngine(thresholds)

    att_concerns, att_summary = engine.evaluate_attendance(att_records)
    asm_concerns, asm_summary = engine.evaluate_assessments(asm_records)
    asg_concerns, asg_summary = engine.evaluate_assignments(asg_records)

    all_concerns = att_concerns + asm_concerns + asg_concerns
    support_priority = engine.determine_overall_support_priority(all_concerns)

    return {
        "success": True,
        "student_id": student_id,
        "profile": profile,
        "indicators": {
            "attendance": att_summary,
            "assessments": asm_summary,
            "assignments": asg_summary,
        },
        "concerns": all_concerns,
        "support_priority": support_priority,
        "requires_support": len(all_concerns) > 0,
        "concerns_count": len(all_concerns),
    }


def validate_intervention_plan(
    student_id: str,
    intervention_plan: List[Dict[str, Any]],
    indicators: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate that proposed interventions are grounded in evidence and logically consistent.

    Critic validation checks:
    - Every intervention addresses a real identified concern.
    - Responsible academic role is specified.
    - Suggested review period is defined.
    - Measurable follow-up outcome is provided.
    - No unsupported claims or hallucinated concerns.
    """
    errors = []
    warnings = []

    if not isinstance(intervention_plan, list):
        return {
            "valid": False,
            "errors": ["Intervention plan must be a list of intervention items."],
            "warnings": [],
        }

    known_concerns = indicators.get("concerns", [])
    known_concern_types = {c.get("concern_type") for c in known_concerns}
    requires_support = indicators.get("requires_support", False)

    if requires_support and len(intervention_plan) == 0:
        errors.append("Student has identified academic concerns, but 0 interventions were planned.")

    if not requires_support and len(intervention_plan) > 0:
        warnings.append(
            "Student has no identified academic concerns, but intervention actions were proposed."
        )

    for idx, item in enumerate(intervention_plan):
        prefix = f"Intervention #{idx + 1}"
        concern = item.get("concern", "").strip()
        action = item.get("recommended_action", "").strip()
        role = item.get("responsible_role", "").strip()
        review = item.get("suggested_review_period", "").strip()
        outcome = item.get("measurable_outcome", "").strip()
        c_type = item.get("concern_type", "")

        if not concern:
            errors.append(f"{prefix}: Missing concern description.")
        if not action:
            errors.append(f"{prefix}: Missing recommended action.")
        if not role:
            errors.append(f"{prefix}: Missing responsible academic role.")
        if not review:
            errors.append(f"{prefix}: Missing suggested review period.")
        if not outcome:
            errors.append(f"{prefix}: Missing measurable follow-up outcome.")

        allowed_meta_types = {"GENERAL_MONITORING", "COORDINATED_SUPPORT"}
        if c_type and c_type not in known_concern_types and c_type not in allowed_meta_types:
            errors.append(
                f"{prefix}: Claims concern type '{c_type}' which was not identified in student indicators."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checked_items": len(intervention_plan),
    }
