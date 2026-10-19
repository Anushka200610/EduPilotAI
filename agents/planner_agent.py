"""Academic Planning Agent for EduPilot AI.

Responsible for:
- Interpreting the incoming analysis request.
- Validating requested student or batch identifiers.
- Determining required academic indicators and tools.
- Formulating an ordered, typed execution plan that guides the LangGraph workflow.
"""

import re
from typing import Any, Dict, List, Optional
from config.settings import settings


class AcademicPlanningAgent:
    """Goal-Based Agent (Russell & Norvig AI Agent Taxonomy).
    
    Operates by combining current percepts with explicit goal states
    to formulate ordered action sequences (planning & sub-goal decomposition).
    """

    def __init__(self):
        self.name = "Academic Planning Agent"
        self.role = "Workflow Planner & Indicator Specifier"
        self.agent_type = "Goal-Based Agent"
        self.taxonomy_class = "Goal-Based Agent (Russell & Norvig AI Taxonomy)"
        self.peas_profile = {
            "Performance Measure": "Goal completeness, indicator coverage, plan execution fidelity",
            "Environment": "Academic records registry, student request parameters",
            "Actuators": "Typed 6-step execution plan, indicator calculation schema",
            "Sensors": "Student ID query, analysis objective string",
        }

    def validate_identifier_format(self, student_id: str) -> bool:
        """Check whether the student identifier matches standard format (e.g. STU1001)."""
        if not student_id or not isinstance(student_id, str):
            return False
        clean_id = student_id.strip().upper()
        # Matches STU followed by 3 to 6 digits
        return bool(re.match(r"^STU\d{3,6}$", clean_id))

    def create_execution_plan(
        self, student_id: str, analysis_objective: Optional[str] = None
    ) -> Dict[str, Any]:
        """Construct a structured, ordered execution plan for student analysis."""
        clean_id = student_id.strip().upper() if student_id else "UNKNOWN"
        objective = (
            analysis_objective
            or "Comprehensive Academic Performance Review and Early Intervention Screening"
        )

        steps = [
            {
                "step_index": 1,
                "step_id": "STEP_INPUT_VALIDATION",
                "name": "Student Identifier & Dataset Validation",
                "agent": "System Validator",
                "agent_type": "Deterministic Gateway",
                "required_tools": ["validate_student_id_exists"],
                "expected_output": "Verified student existence in synthetic registry.",
                "status": "COMPLETED",
            },
            {
                "step_index": 2,
                "step_id": "STEP_DATA_RETRIEVAL",
                "name": "Retrieve Academic Records via MCP",
                "agent": "Student Analytics Agent",
                "agent_type": "Model-Based Reflex Agent",
                "required_tools": [
                    "get_student_profile",
                    "get_attendance_history",
                    "get_assessment_results",
                    "get_assignment_status",
                ],
                "expected_output": "Structured raw records across all enrolled subjects.",
                "status": "PENDING",
            },
            {
                "step_index": 3,
                "step_id": "STEP_INDICATOR_CALCULATION",
                "name": "Calculate Academic Indicators & Evaluate Thresholds",
                "agent": "Student Analytics Agent",
                "agent_type": "Model-Based Reflex Agent",
                "required_tools": ["calculate_academic_indicators"],
                "expected_output": "Aggregated attendance %, marks %, trend deltas, and flagged concerns.",
                "status": "PENDING",
            },
            {
                "step_index": 4,
                "step_id": "STEP_INTERVENTION_FORMULATION",
                "name": "Synthesize Targeted Interventions",
                "agent": "Intervention Planning Agent",
                "agent_type": "Utility-Based Agent",
                "required_tools": ["decision_rules_mapping"],
                "expected_output": "Prioritized interventions with roles, review periods, and measurable outcomes.",
                "status": "PENDING",
            },
            {
                "step_index": 5,
                "step_id": "STEP_CRITIC_VALIDATION",
                "name": "Independent Calculation Recomputation & Grounding Audit",
                "agent": "Critic and Validation Agent",
                "agent_type": "Learning & Verification Agent",
                "required_tools": ["validate_intervention_plan"],
                "expected_output": "Verification pass/fail status, invariant check results, error list.",
                "status": "PENDING",
            },
            {
                "step_index": 6,
                "step_id": "STEP_REPORT_GENERATION",
                "name": "Assemble 18-Field Academic Intervention Report",
                "agent": "Report Generator Node",
                "agent_type": "Standardized Assembly Element",
                "required_tools": ["generate_structured_report"],
                "expected_output": "Final structured report marked VALIDATED, NEEDS_REVIEW, or VALIDATION_FAILED.",
                "status": "PENDING",
            },
        ]

        return {
            "plan_id": f"PLAN-{clean_id}",
            "student_id": clean_id,
            "objective": objective,
            "term": settings.academic_term,
            "indicators_to_compute": [
                "Overall Attendance Percentage",
                "Subject-wise Attendance Distribution",
                "Assessment Average & Passing Marks Compliance",
                "Sequential Assessment Trend (Score Delta)",
                "Assignment Completion Rate & Missing Submissions",
                "Composite Support Priority (HIGH, MEDIUM, LOW, NONE)",
            ],
            "total_steps": len(steps),
            "steps": steps,
        }


# Singleton instance
planner_agent = AcademicPlanningAgent()
