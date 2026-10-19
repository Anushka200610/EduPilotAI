"""Critic and Validation Agent for EduPilot AI.

Responsible for:
- Independently recomputing attendance percentages, marks, and trends.
- Verifying mathematical invariants (attended <= held, 0 <= marks <= max_marks).
- Verifying that configured thresholds were applied strictly and correctly.
- Auditing intervention plans against evidence to prevent hallucinated claims.
- Returning structured validation errors to trigger graph correction nodes when needed.
"""

from typing import Any, Dict, List
from config.settings import AcademicThresholds, settings
from tools.academic_tools import validate_intervention_plan
from tools.decision_rules import DecisionRulesEngine


class CriticAndValidationAgent:
    """Learning & Verification Agent (Russell & Norvig AI Agent Taxonomy).

    Acts as the Critic Element in a learning framework: evaluates agent
    performance against mathematical invariants and ground-truth standards,
    providing error feedback to drive state correction and bounded learning retries.
    """

    def __init__(self, thresholds: AcademicThresholds = settings.thresholds):
        self.name = "Critic and Validation Agent"
        self.role = "Independent Auditor & Verification Critic"
        self.agent_type = "Learning & Verification Agent"
        self.taxonomy_class = "Learning & Verification Agent (Russell & Norvig AI Taxonomy)"
        self.thresholds = thresholds
        self.peas_profile = {
            "Performance Measure": "Verification accuracy, invariant breach detection, zero hallucination tolerance",
            "Environment": "Agent outputs, raw ground-truth datasets, institutional invariant rules",
            "Actuators": "Validation status flag (PASSED/FAILED), error discrepancy log, correction signals",
            "Sensors": "Computed indicators, drafted interventions, raw dataset rows",
        }

    def validate_analysis(
        self,
        student_id: str,
        indicators: Dict[str, Any],
        concerns: List[Dict[str, Any]],
        interventions: List[Dict[str, Any]],
        raw_attendance: List[Dict[str, Any]],
        raw_assessments: List[Dict[str, Any]],
        raw_assignments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Perform comprehensive independent verification of calculations, rules, and interventions."""
        errors: List[str] = []
        checks_performed: List[Dict[str, Any]] = []

        # 1. Independent Attendance Recomputation
        total_held = 0
        total_attended = 0
        for rec in raw_attendance:
            subj = rec.get("subject_id", "UNKNOWN")
            held = int(rec.get("classes_held", 0))
            attended = int(rec.get("classes_attended", 0))

            if attended > held:
                errors.append(f"Invariant violation in {subj}: attended ({attended}) > held ({held}).")
            if held < 0 or attended < 0:
                errors.append(f"Invariant violation in {subj}: negative attendance values.")

            total_held += held
            total_attended += attended

            if held > 0:
                expected_pct = round((attended / held) * 100.0, 2)
                # Verify threshold check
                has_att_concern = any(
                    c.get("concern_type") == "ATTENDANCE_LOW" and c.get("subject_id") == subj
                    for c in concerns
                )
                if expected_pct < self.thresholds.min_attendance_pct and not has_att_concern:
                    errors.append(
                        f"False Negative: {subj} attendance is {expected_pct}% (<{self.thresholds.min_attendance_pct}%), but was not flagged."
                    )
                elif expected_pct >= self.thresholds.min_attendance_pct and has_att_concern:
                    errors.append(
                        f"False Positive: {subj} attendance is {expected_pct}% (>={self.thresholds.min_attendance_pct}%), but was flagged as low."
                    )

        checks_performed.append({
            "check": "Attendance Invariants & Threshold Recomputation",
            "passed": not any("attendance" in e.lower() for e in errors),
            "subjects_verified": len(raw_attendance),
        })

        # 2. Independent Assessment Recomputation
        by_subj: Dict[str, List[Dict[str, Any]]] = {}
        for rec in raw_assessments:
            subj = rec.get("subject_id", "UNKNOWN")
            by_subj.setdefault(subj, []).append(rec)
            marks = float(rec.get("marks_obtained", 0))
            max_marks = float(rec.get("maximum_marks", 100))
            name = rec.get("assessment_name", "")

            if marks < 0 or marks > max_marks:
                errors.append(f"Invariant violation in {subj} ({name}): marks ({marks}) outside [0, {max_marks}].")

            if max_marks > 0:
                pct = round((marks / max_marks) * 100.0, 2)
                has_perf_concern = any(
                    c.get("concern_type") == "ACADEMIC_PERFORMANCE_LOW"
                    and c.get("subject_id") == subj
                    and name in c.get("description", "")
                    for c in concerns
                )
                if pct < self.thresholds.min_passing_marks_pct and not has_perf_concern:
                    errors.append(
                        f"False Negative: {subj} ({name}) score is {pct}% (<{self.thresholds.min_passing_marks_pct}%), but was not flagged."
                    )
                elif pct >= self.thresholds.min_passing_marks_pct and has_perf_concern:
                    errors.append(
                        f"False Positive: {subj} ({name}) score is {pct}% (>={self.thresholds.min_passing_marks_pct}%), but was flagged as low."
                    )

        # 3. Assessment Trend Verification
        for subj, recs in by_subj.items():
            if len(recs) >= 2:
                sorted_recs = sorted(recs, key=lambda x: x.get("assessment_date", ""))
                q1_pct = round((float(sorted_recs[0]["marks_obtained"]) / float(sorted_recs[0]["maximum_marks"])) * 100.0, 2)
                mid_pct = round((float(sorted_recs[1]["marks_obtained"]) / float(sorted_recs[1]["maximum_marks"])) * 100.0, 2)
                delta = q1_pct - mid_pct
                has_decline_concern = any(
                    c.get("concern_type") == "PERFORMANCE_DECLINE" and c.get("subject_id") == subj
                    for c in concerns
                )
                if delta >= self.thresholds.decline_threshold_pct and not has_decline_concern:
                    errors.append(
                        f"False Negative: Score drop in {subj} is {delta:.1f}% pts (>= {self.thresholds.decline_threshold_pct}%), but was not flagged."
                    )
                elif delta < self.thresholds.decline_threshold_pct and has_decline_concern:
                    errors.append(
                        f"False Positive: Score drop in {subj} is {delta:.1f}% pts (< {self.thresholds.decline_threshold_pct}%), but was flagged."
                    )

        checks_performed.append({
            "check": "Assessment Invariants & Trajectory Recomputation",
            "passed": not any("score" in e.lower() or "marks" in e.lower() for e in errors),
            "assessments_verified": len(raw_assessments),
        })

        # 4. Independent Assignment Audit
        missing_count = sum(
            1 for a in raw_assignments if str(a.get("submission_status", "")).upper() in ["MISSING", "PENDING"]
        )
        has_asg_concern = any(c.get("concern_type") == "ASSIGNMENT_INCOMPLETE" for c in concerns)
        if missing_count > self.thresholds.max_missing_assignments and not has_asg_concern:
            errors.append(
                f"False Negative: {missing_count} missing assignments (> {self.thresholds.max_missing_assignments}), but was not flagged."
            )
        elif missing_count <= self.thresholds.max_missing_assignments and has_asg_concern:
            errors.append(
                f"False Positive: {missing_count} missing assignments, but flagged as assignment concern."
            )

        checks_performed.append({
            "check": "Assignment Completion Audit",
            "passed": not any("assignment" in e.lower() for e in errors),
            "assignments_verified": len(raw_assignments),
        })

        # 5. Intervention Plan Grounding & Integrity Check
        plan_validation = validate_intervention_plan(
            student_id=student_id,
            intervention_plan=interventions,
            indicators={"concerns": concerns, "requires_support": len(concerns) > 0},
        )
        if not plan_validation.get("valid", False):
            errors.extend(plan_validation.get("errors", []))

        checks_performed.append({
            "check": "Intervention Grounding & Actionability",
            "passed": plan_validation.get("valid", False),
            "checked_items": len(interventions),
        })

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "checks_performed": checks_performed,
            "timestamp": DecisionRulesEngine.calculate_attendance_percentage.__name__,
            "total_checks": len(checks_performed),
            "passed_checks": sum(1 for c in checks_performed if c.get("passed", False)),
        }


# Singleton instance
critic_agent = CriticAndValidationAgent()
