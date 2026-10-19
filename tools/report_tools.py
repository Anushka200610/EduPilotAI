"""Report Tools for EduPilot AI.

Generates, validates, and serializes the 18-field standardized Academic Intervention Report.
Provides JSON serialization, CSV export, and Markdown rendering.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from config.settings import REPORTS_DIR, settings


def generate_structured_report(
    student_id: str,
    academic_term: Optional[str] = None,
    analysis_objective: Optional[str] = None,
    execution_plan: Optional[List[Dict[str, Any]]] = None,
    indicators: Optional[Dict[str, Any]] = None,
    concerns: Optional[List[Dict[str, Any]]] = None,
    interventions: Optional[List[Dict[str, Any]]] = None,
    critic_validation: Optional[Dict[str, Any]] = None,
    missing_data_notes: Optional[List[str]] = None,
    status_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Assemble the comprehensive 18-field Academic Intervention Report."""
    now_iso = datetime.now(timezone.utc).isoformat()
    now_tag = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    clean_id = student_id.strip().upper()
    report_id = f"RPT-{clean_id}-{now_tag}"

    indicators = indicators or {}
    concerns = concerns or []
    interventions = interventions or []
    critic_validation = critic_validation or {"valid": False, "errors": ["Validation was not executed."]}
    missing_data_notes = missing_data_notes or []

    # Determine final status
    if status_override:
        final_status = status_override
    elif not critic_validation.get("valid", False):
        if critic_validation.get("retry_exhausted", False):
            final_status = "NEEDS_REVIEW"
        else:
            final_status = "VALIDATION_FAILED"
    else:
        final_status = "VALIDATED"

    # Compile primary roles, timeline, and measurable outcomes across interventions
    roles = sorted(list({item.get("responsible_role") for item in interventions if item.get("responsible_role")}))
    review_periods = sorted(list({item.get("suggested_review_period") for item in interventions if item.get("suggested_review_period")}))
    outcomes = [item.get("measurable_outcome") for item in interventions if item.get("measurable_outcome")]

    # Supporting evidence compilation
    evidence_list = []
    for c in concerns:
        evidence_list.append({
            "concern": c.get("description", ""),
            "rule": c.get("rule_name", ""),
            "evidence": c.get("evidence", ""),
            "severity": c.get("severity", "MEDIUM"),
        })

    # The 18 standard fields
    report = {
        "report_id": report_id,                                           # 1
        "timestamp": now_iso,                                             # 2
        "student_id": clean_id,                                           # 3
        "academic_term": academic_term or settings.academic_term,         # 4
        "analysis_objective": (                                           # 5
            analysis_objective or "Comprehensive Academic Performance Review and Early Intervention Screening"
        ),
        "execution_plan": execution_plan or [],                           # 6
        "attendance_indicators": indicators.get("attendance", {}),        # 7
        "assessment_indicators": indicators.get("assessments", {}),       # 8
        "assignment_indicators": indicators.get("assignments", {}),       # 9
        "identified_concerns": concerns,                                  # 10
        "supporting_evidence": evidence_list,                             # 11
        "recommended_interventions": interventions,                       # 12
        "responsible_academic_role": ", ".join(roles) if roles else "Faculty Mentor / Academic Advisor", # 13
        "suggested_review_period": "; ".join(review_periods) if review_periods else "4 Weeks",           # 14
        "expected_measurable_outcome": outcomes,                          # 15
        "missing_data_and_limitations": missing_data_notes + [            # 16
            "Decision support PoC based on synthetic records. Human faculty review is required before action."
        ],
        "critic_validation_results": critic_validation,                   # 17
        "final_status": final_status,                                     # 18
    }

    return report


def save_report_to_json(report: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """Save report dict to JSON file."""
    if output_path is None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_id = report.get("report_id", f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        output_path = REPORTS_DIR / f"{report_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return output_path


def export_reports_to_dataframe(reports: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a batch of reports to a tabular DataFrame for export."""
    rows = []
    for r in reports:
        att = r.get("attendance_indicators", {})
        asm = r.get("assessment_indicators", {})
        asg = r.get("assignment_indicators", {})
        concerns = r.get("identified_concerns", [])
        interventions = r.get("recommended_interventions", [])
        validation = r.get("critic_validation_results", {})

        rows.append({
            "report_id": r.get("report_id"),
            "student_id": r.get("student_id"),
            "academic_term": r.get("academic_term"),
            "timestamp": r.get("timestamp"),
            "overall_attendance_pct": att.get("overall_pct", 0.0),
            "assessment_average_pct": asm.get("overall_average_pct", 0.0),
            "assignment_completion_pct": asg.get("completion_pct", 0.0),
            "concerns_count": len(concerns),
            "concerns_summary": "; ".join([c.get("rule_name", "") for c in concerns]),
            "interventions_count": len(interventions),
            "validation_passed": validation.get("valid", False),
            "final_status": r.get("final_status"),
            "responsible_role": r.get("responsible_academic_role"),
        })

    return pd.DataFrame(rows)
