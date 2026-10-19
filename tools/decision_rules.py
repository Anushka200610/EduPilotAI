"""Configurable Decision Rules for EduPilot AI.

Implements transparent, deterministic decision rules to detect academic concerns,
evaluate thresholds, calculate percentage metrics safely, and assemble
verifiable supporting evidence.
"""

from typing import Any, Dict, List, Optional, Tuple
from config.settings import AcademicThresholds, settings


class DecisionRulesEngine:
    """Deterministic evaluation engine using transparent academic rules."""

    def __init__(self, thresholds: Optional[AcademicThresholds] = None):
        self.thresholds = thresholds or settings.thresholds

    @staticmethod
    def calculate_attendance_percentage(classes_attended: int, classes_held: int) -> float:
        """Calculate attendance percentage with strict boundary checks.

        Formula: (classes_attended / classes_held) * 100
        """
        if classes_held < 0 or classes_attended < 0:
            raise ValueError(f"Negative values not allowed: attended={classes_attended}, held={classes_held}")
        if classes_attended > classes_held:
            raise ValueError(
                f"Classes attended ({classes_attended}) cannot exceed classes held ({classes_held})"
            )
        if classes_held == 0:
            return 0.0
        return round((classes_attended / classes_held) * 100.0, 2)

    @staticmethod
    def calculate_marks_percentage(marks_obtained: float, maximum_marks: float) -> float:
        """Calculate marks percentage with strict range checks.

        Formula: (marks_obtained / maximum_marks) * 100
        """
        if maximum_marks <= 0:
            raise ValueError(f"Maximum marks must be positive, got {maximum_marks}")
        if marks_obtained < 0 or marks_obtained > maximum_marks:
            raise ValueError(
                f"Marks obtained ({marks_obtained}) must be within [0, {maximum_marks}]"
            )
        return round((marks_obtained / maximum_marks) * 100.0, 2)

    def evaluate_attendance(
        self, attendance_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Evaluate attendance records against configured thresholds.

        Returns:
            concerns: List of identified concern objects
            summary: Aggregated attendance statistics
        """
        concerns = []
        if not attendance_records:
            concerns.append({
                "concern_type": "DATA_INCOMPLETE",
                "severity": "HIGH",
                "rule_name": "RULE_ATTENDANCE_RECORD_MISSING",
                "description": "No attendance records found for this student.",
                "evidence": "Attendance dataset returned 0 records.",
            })
            return concerns, {"overall_pct": 0.0, "total_attended": 0, "total_held": 0, "subjects": {}}

        total_held = 0
        total_attended = 0
        subject_stats = {}

        for rec in attendance_records:
            subj = rec.get("subject_id", "UNKNOWN")
            held = int(rec.get("classes_held", 0))
            attended = int(rec.get("classes_attended", 0))

            try:
                pct = self.calculate_attendance_percentage(attended, held)
            except ValueError as e:
                concerns.append({
                    "concern_type": "DATA_INVALID",
                    "severity": "CRITICAL",
                    "rule_name": "RULE_ATTENDANCE_INVARIANT_VIOLATION",
                    "description": f"Invalid attendance record in subject {subj}: {str(e)}",
                    "evidence": f"held={held}, attended={attended}",
                })
                continue

            total_held += held
            total_attended += attended
            subject_stats[subj] = {
                "classes_held": held,
                "classes_attended": attended,
                "percentage": pct,
                "below_threshold": pct < self.thresholds.min_attendance_pct,
            }

            # Subject-level attendance check
            if pct < self.thresholds.min_attendance_pct:
                severity = "HIGH" if pct < self.thresholds.critical_attendance_pct else "MEDIUM"
                concerns.append({
                    "concern_type": "ATTENDANCE_LOW",
                    "severity": severity,
                    "rule_name": "RULE_ATTENDANCE_BELOW_MINIMUM",
                    "subject_id": subj,
                    "description": (
                        f"Attendance in {subj} is {pct:.1f}%, below the minimum "
                        f"required threshold of {self.thresholds.min_attendance_pct:.1f}%."
                    ),
                    "evidence": f"{attended}/{held} classes attended ({pct:.1f}%) in {subj}.",
                    "metric_value": pct,
                    "threshold_value": self.thresholds.min_attendance_pct,
                })

        overall_pct = (
            round((total_attended / total_held) * 100.0, 2) if total_held > 0 else 0.0
        )

        # Overall attendance check (if multiple subjects exist and overall is low)
        if len(subject_stats) > 1 and overall_pct < self.thresholds.min_attendance_pct:
            # Check if not already covered or emphasize aggregate
            pass

        summary = {
            "overall_pct": overall_pct,
            "total_attended": total_attended,
            "total_held": total_held,
            "subjects": subject_stats,
        }
        return concerns, summary

    def evaluate_assessments(
        self, assessment_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Evaluate assessment records for low marks and declining trajectories."""
        concerns = []
        if not assessment_records:
            concerns.append({
                "concern_type": "DATA_INCOMPLETE",
                "severity": "HIGH",
                "rule_name": "RULE_ASSESSMENT_RECORD_MISSING",
                "description": "No assessment records found for this student.",
                "evidence": "Assessment dataset returned 0 records.",
            })
            return concerns, {"overall_average_pct": 0.0, "subjects": {}}

        # Group by subject
        by_subject: Dict[str, List[Dict[str, Any]]] = {}
        for rec in assessment_records:
            subj = rec.get("subject_id", "UNKNOWN")
            by_subject.setdefault(subj, []).append(rec)

        subject_stats = {}
        all_percentages = []

        for subj, recs in by_subject.items():
            subj_scores = []
            valid_recs = []

            for r in recs:
                marks = float(r.get("marks_obtained", 0))
                max_marks = float(r.get("maximum_marks", 100))
                name = r.get("assessment_name", "Assessment")
                date = r.get("assessment_date", "")

                try:
                    pct = self.calculate_marks_percentage(marks, max_marks)
                except ValueError as e:
                    concerns.append({
                        "concern_type": "DATA_INVALID",
                        "severity": "CRITICAL",
                        "rule_name": "RULE_ASSESSMENT_INVARIANT_VIOLATION",
                        "description": f"Invalid marks entry in {subj} ({name}): {str(e)}",
                        "evidence": f"marks={marks}, max_marks={max_marks}",
                    })
                    continue

                subj_scores.append(pct)
                all_percentages.append(pct)
                valid_recs.append({
                    "name": name,
                    "marks": marks,
                    "max_marks": max_marks,
                    "pct": pct,
                    "date": date,
                })

                # Check individual assessment failure
                if pct < self.thresholds.min_passing_marks_pct:
                    severity = "HIGH" if pct < self.thresholds.critical_marks_pct else "MEDIUM"
                    concerns.append({
                        "concern_type": "ACADEMIC_PERFORMANCE_LOW",
                        "severity": severity,
                        "rule_name": "RULE_ASSESSMENT_BELOW_PASSING",
                        "subject_id": subj,
                        "description": (
                            f"Score of {pct:.1f}% in {subj} ({name}) is below the "
                            f"passing threshold of {self.thresholds.min_passing_marks_pct:.1f}%."
                        ),
                        "evidence": f"Obtained {marks}/{max_marks} marks ({pct:.1f}%) in {name}.",
                        "metric_value": pct,
                        "threshold_value": self.thresholds.min_passing_marks_pct,
                    })

            # Check Trend / Decline across sequential assessments
            if len(valid_recs) >= 2:
                # Sort by date
                valid_recs.sort(key=lambda x: x["date"])
                for k in range(len(valid_recs) - 1):
                    first = valid_recs[k]
                    second = valid_recs[k + 1]
                    delta = first["pct"] - second["pct"]

                    if delta >= self.thresholds.decline_threshold_pct:
                        concerns.append({
                            "concern_type": "PERFORMANCE_DECLINE",
                            "severity": "HIGH" if delta >= 25.0 else "MEDIUM",
                            "rule_name": "RULE_ASSESSMENT_SCORE_DECLINE",
                            "subject_id": subj,
                            "description": (
                                f"Performance decline of {delta:.1f} percentage points observed "
                                f"in {subj} from {first['name']} ({first['pct']:.1f}%) to {second['name']} ({second['pct']:.1f}%)."
                            ),
                            "evidence": (
                                f"{first['name']}: {first['marks']}/{first['max_marks']} ({first['pct']:.1f}%) -> "
                                f"{second['name']}: {second['marks']}/{second['max_marks']} ({second['pct']:.1f}%). Drop = {delta:.1f}% pts."
                            ),
                            "metric_value": delta,
                            "threshold_value": self.thresholds.decline_threshold_pct,
                        })

            avg_pct = round(sum(subj_scores) / len(subj_scores), 2) if subj_scores else 0.0
            subject_stats[subj] = {
                "assessments": valid_recs,
                "average_pct": avg_pct,
                "lowest_pct": min(subj_scores) if subj_scores else 0.0,
            }

        overall_avg = round(sum(all_percentages) / len(all_percentages), 2) if all_percentages else 0.0
        return concerns, {"overall_average_pct": overall_avg, "subjects": subject_stats}

    def evaluate_assignments(
        self, assignment_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Evaluate assignment completion and submission status."""
        concerns = []
        if not assignment_records:
            concerns.append({
                "concern_type": "DATA_INCOMPLETE",
                "severity": "HIGH",
                "rule_name": "RULE_ASSIGNMENT_RECORD_MISSING",
                "description": "No assignment records found for this student.",
                "evidence": "Assignment dataset returned 0 records.",
            })
            return concerns, {"total": 0, "submitted": 0, "late": 0, "missing": 0, "completion_pct": 0.0}

        total = len(assignment_records)
        submitted = 0
        late = 0
        missing = 0
        missing_details = []

        for r in assignment_records:
            status = str(r.get("submission_status", "UNKNOWN")).upper().strip()
            subj = r.get("subject_id", "")
            asg_id = r.get("assignment_id", "")

            if status == "SUBMITTED":
                submitted += 1
            elif status == "LATE":
                late += 1
            elif status in ["MISSING", "PENDING"]:
                missing += 1
                missing_details.append(f"{asg_id} ({subj})")
            else:
                missing += 1
                missing_details.append(f"{asg_id} ({subj}) [status: {status}]")

        completion_pct = round(((submitted + late) / total) * 100.0, 2) if total > 0 else 0.0

        if missing > self.thresholds.max_missing_assignments:
            severity = "HIGH" if missing >= 3 else "MEDIUM"
            concerns.append({
                "concern_type": "ASSIGNMENT_INCOMPLETE",
                "severity": severity,
                "rule_name": "RULE_ASSIGNMENT_MISSING_COUNT",
                "description": (
                    f"Student has {missing} missing/unsubmitted assignment(s), "
                    f"exceeding threshold of {self.thresholds.max_missing_assignments}."
                ),
                "evidence": f"Missing assignments: {', '.join(missing_details)}. Completion rate: {completion_pct:.1f}%.",
                "metric_value": missing,
                "threshold_value": self.thresholds.max_missing_assignments,
            })

        summary = {
            "total": total,
            "submitted": submitted,
            "late": late,
            "missing": missing,
            "completion_pct": completion_pct,
            "missing_list": missing_details,
        }
        return concerns, summary

    def determine_overall_support_priority(self, concerns: List[Dict[str, Any]]) -> str:
        """Compute the composite priority rating based on identified concerns."""
        if not concerns:
            return "NONE"

        has_critical = any(c.get("severity") in ["CRITICAL", "HIGH"] for c in concerns)
        # Check if multiple distinct concern types exist
        unique_types = {c.get("concern_type") for c in concerns if c.get("concern_type") != "DATA_INCOMPLETE"}

        if len(unique_types) >= 2 or has_critical:
            return "HIGH"
        elif len(concerns) >= 1:
            return "MEDIUM"
        return "LOW"
