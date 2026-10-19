"""Student Analytics Agent for EduPilot AI.

Responsible for:
- Retrieving academic records via MCP client tools.
- Calculating attendance, assessment performance, and assignment status.
- Comparing sequential assessments when sufficient history exists.
- Assembling strict, traceable evidence for every flagged concern.
- Reporting missing or invalid data explicitly without hallucination.
"""

from typing import Any, Dict, List
from mcp_server.client import mcp_client


class StudentAnalyticsAgent:
    """Model-Based Reflex Agent (Russell & Norvig AI Agent Taxonomy).

    Operates using condition-action rules coupled with an internal state
    tracking chronological history (consecutive quiz & exam scores, past attendance).
    """

    def __init__(self):
        self.name = "Student Analytics Agent"
        self.role = "Data Retrieval & Academic Performance Analyst"
        self.agent_type = "Model-Based Reflex Agent"
        self.taxonomy_class = "Model-Based Reflex Agent (Russell & Norvig AI Taxonomy)"
        self.peas_profile = {
            "Performance Measure": "Accuracy of computed indicators, rule triggering precision, evidence grounding",
            "Environment": "Academic database (attendance, assessments, assignments via MCP tools)",
            "Actuators": "Calculated indicators dict, flagged concerns list, traceable evidence records",
            "Sensors": "MCP tool payloads (get_attendance_history, get_assessment_results, get_assignment_status)",
        }

    def analyze_student(self, student_id: str) -> Dict[str, Any]:
        """Execute full analytics pipeline for a given student via MCP tools."""
        clean_id = student_id.strip().upper()

        # Call MCP calculation tool
        result = mcp_client.calculate_academic_indicators(clean_id)

        if not result.get("success", False):
            # Error or unknown student
            error_msg = result.get("error", f"Analytics failed for student {clean_id}")
            return {
                "success": False,
                "error": error_msg,
                "indicators": {},
                "concerns": [
                    {
                        "concern_type": "DATA_INCOMPLETE",
                        "severity": "CRITICAL",
                        "rule_name": "RULE_STUDENT_DATA_UNAVAILABLE",
                        "description": error_msg,
                        "evidence": f"Failed MCP tool call for {clean_id}: {error_msg}",
                    }
                ],
                "evidence_summary": {},
                "support_priority": "HIGH",
            }

        profile = result.get("profile", {})
        indicators = result.get("indicators", {})
        concerns = result.get("concerns", [])
        support_priority = result.get("support_priority", "NONE")

        # Compile structured evidence summary for each concern
        evidence_summary = {
            "student_id": clean_id,
            "overall_attendance_pct": indicators.get("attendance", {}).get("overall_pct", 0.0),
            "assessment_average_pct": indicators.get("assessments", {}).get("overall_average_pct", 0.0),
            "assignment_completion_pct": indicators.get("assignments", {}).get("completion_pct", 0.0),
            "flagged_concerns_count": len(concerns),
            "traceable_findings": [],
        }

        for c in concerns:
            evidence_summary["traceable_findings"].append({
                "rule": c.get("rule_name"),
                "concern_type": c.get("concern_type"),
                "severity": c.get("severity"),
                "subject_id": c.get("subject_id", "GENERAL"),
                "finding": c.get("description"),
                "verifiable_evidence": c.get("evidence"),
            })

        return {
            "success": True,
            "student_id": clean_id,
            "profile": profile,
            "indicators": indicators,
            "concerns": concerns,
            "evidence_summary": evidence_summary,
            "support_priority": support_priority,
        }


# Singleton instance
analytics_agent = StudentAnalyticsAgent()
