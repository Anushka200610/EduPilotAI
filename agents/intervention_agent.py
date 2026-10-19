"""Intervention Planning Agent for EduPilot AI.

Responsible for:
- Mapping identified concerns into targeted, pedagogically sound interventions.
- Applying transparent, configurable decision rules.
- Assigning responsible academic roles, suggested review periods, and measurable outcomes.
- Prioritizing support based on evidence severity.
- Maintaining decision-support boundaries without making punitive automated decisions.
"""

from typing import Any, Dict, List


class InterventionPlanningAgent:
    """Utility-Based Agent (Russell & Norvig AI Agent Taxonomy).

    Evaluates academic recovery utility U(Action, Severity, Urgency) to
    maximize student success payoffs while balancing intervention intensity and roles.
    """

    def __init__(self):
        self.name = "Intervention Planning Agent"
        self.role = "Academic Support & Remediation Strategist"
        self.agent_type = "Utility-Based Agent"
        self.taxonomy_class = "Utility-Based Agent (Russell & Norvig AI Taxonomy)"
        self.peas_profile = {
            "Performance Measure": "Utility maximization (targeted support vs academic burden, milestone clarity)",
            "Environment": "Identified academic concerns, institutional support structures",
            "Actuators": "Prioritized intervention plans, assigned academic roles, review timelines, measurable goals",
            "Sensors": "Concerns list, severity levels, support priority rating (HIGH/MEDIUM/LOW)",
        }

    def formulate_interventions(
        self,
        student_id: str,
        concerns: List[Dict[str, Any]],
        indicators: Dict[str, Any],
        support_priority: str,
    ) -> List[Dict[str, Any]]:
        """Formulate prioritized academic intervention recommendations."""
        clean_id = student_id.strip().upper()
        interventions = []

        if not concerns:
            # Positive reinforcement / enrichment for students without academic concerns
            interventions.append({
                "concern": "Satisfactory Academic Progress (No flagged concerns)",
                "concern_type": "GENERAL_MONITORING",
                "severity": "INFO",
                "supporting_evidence": (
                    f"Overall attendance: {indicators.get('attendance', {}).get('overall_pct', 0.0)}%, "
                    f"Assessment average: {indicators.get('assessments', {}).get('overall_average_pct', 0.0)}%, "
                    f"Assignment completion: {indicators.get('assignments', {}).get('completion_pct', 0.0)}%."
                ),
                "recommended_action": (
                    "Maintain current study routine. Recommend invitation to peer-assisted study sessions "
                    "or honors project tracks to foster academic leadership."
                ),
                "responsible_role": "Faculty Mentor",
                "suggested_review_period": "End-of-Semester Review",
                "measurable_outcome": "Maintain >=75% attendance and current assessment trajectory in all courses.",
            })
            return interventions

        # Map each concern to a targeted intervention
        for c in concerns:
            c_type = c.get("concern_type", "GENERAL")
            subj = c.get("subject_id", "General")
            evidence = c.get("evidence", "Recorded in synthetic dataset.")
            severity = c.get("severity", "MEDIUM")

            if c_type == "ATTENDANCE_LOW":
                metric_val = c.get("metric_value", 0.0)
                is_crit = metric_val < 65.0
                action = (
                    f"Schedule mandatory 1-on-1 attendance counseling session with {subj} faculty. "
                    "Review schedule conflicts, commute issues, or health reasons. Sign an attendance undertaking."
                )
                if is_crit:
                    action += " Issue early formal alert to academic advisor and student guardian."

                interventions.append({
                    "concern": f"Attendance below 75% in {subj}",
                    "concern_type": "ATTENDANCE_LOW",
                    "severity": severity,
                    "supporting_evidence": evidence,
                    "recommended_action": action,
                    "responsible_role": "Subject Teacher & Faculty Mentor",
                    "suggested_review_period": "2 Weeks",
                    "measurable_outcome": f"Attend >=85% of upcoming lectures in {subj} to raise cumulative attendance towards 75%.",
                })

            elif c_type == "ACADEMIC_PERFORMANCE_LOW":
                interventions.append({
                    "concern": f"Below passing threshold in {subj} assessment",
                    "concern_type": "ACADEMIC_PERFORMANCE_LOW",
                    "severity": severity,
                    "supporting_evidence": evidence,
                    "recommended_action": (
                        f"Provide targeted concept revision worksheets for {subj}. "
                        "Assign a student to a weekly peer tutoring group or faculty office hours for problem-solving reinforcement."
                    ),
                    "responsible_role": f"{subj} Course Instructor",
                    "suggested_review_period": "3 Weeks",
                    "measurable_outcome": f"Achieve >=50% marks in the upcoming diagnostic or tutorial assessment in {subj}.",
                })

            elif c_type == "PERFORMANCE_DECLINE":
                interventions.append({
                    "concern": f"Steep score drop in {subj} examinations",
                    "concern_type": "PERFORMANCE_DECLINE",
                    "severity": severity,
                    "supporting_evidence": evidence,
                    "recommended_action": (
                        f"Conduct diagnostic post-mortem review of Mid-Term exam with student in {subj}. "
                        "Identify foundational knowledge gaps, time management bottlenecks, or exam anxiety."
                    ),
                    "responsible_role": f"{subj} Subject Teacher",
                    "suggested_review_period": "2 Weeks",
                    "measurable_outcome": "Demonstrate score recovery (minimum +10 percentage points) on subsequent quiz.",
                })

            elif c_type == "ASSIGNMENT_INCOMPLETE":
                interventions.append({
                    "concern": "Unsubmitted or missing coursework assignments",
                    "concern_type": "ASSIGNMENT_INCOMPLETE",
                    "severity": severity,
                    "supporting_evidence": evidence,
                    "recommended_action": (
                        "Issue assignment deadline reminder and offer a 5-day makeup submission window "
                        "with structured milestone checkpoints."
                    ),
                    "responsible_role": "Subject Teacher & Teaching Assistant",
                    "suggested_review_period": "1 Week",
                    "measurable_outcome": "Submit 100% of outstanding assignments within the designated makeup window.",
                })

            elif c_type == "DATA_INCOMPLETE":
                interventions.append({
                    "concern": "Incomplete or missing student records in academic registry",
                    "concern_type": "DATA_INCOMPLETE",
                    "severity": severity,
                    "supporting_evidence": evidence,
                    "recommended_action": (
                        "Notify the Academic Department Registry to audit student enrollment status, "
                        "verify attendance logs, and upload missing assessment records."
                    ),
                    "responsible_role": "Department Academic Coordinator",
                    "suggested_review_period": "3 Business Days",
                    "measurable_outcome": "Resolution of missing dataset entries in central database.",
                })

        # Coordinated Meeting for multiple simultaneous concerns or high priority
        unique_types = {c.get("concern_type") for c in concerns if c.get("concern_type") != "DATA_INCOMPLETE"}
        if len(unique_types) >= 2 or support_priority == "HIGH":
            interventions.insert(0, {
                "concern": "Multiple Simultaneous Academic Concerns (Attendance, Marks, or Assignments)",
                "concern_type": "COORDINATED_SUPPORT",
                "severity": "HIGH",
                "supporting_evidence": (
                    f"Student has {len(concerns)} active concerns across multiple categories. "
                    f"Composite support priority evaluated as HIGH."
                ),
                "recommended_action": (
                    "Convene a multi-disciplinary academic advisement meeting involving the Faculty Advisor, "
                    "concerned subject instructors, and the student. Formulate an integrated recovery roadmap."
                ),
                "responsible_role": "Faculty Advisor & Head of Department",
                "suggested_review_period": "2 Weeks",
                "measurable_outcome": "Signed agreement on comprehensive academic recovery plan with bi-weekly check-ins.",
            })

        return interventions


# Singleton instance
intervention_agent = InterventionPlanningAgent()
