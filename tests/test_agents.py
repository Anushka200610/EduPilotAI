"""Tests for the Four Specialized Agents."""

import pytest
from agents.planner_agent import planner_agent
from agents.analytics_agent import analytics_agent
from agents.intervention_agent import intervention_agent
from agents.critic_agent import critic_agent
from services.data_service import data_service


def test_planner_agent_execution_plan():
    """Verify that Academic Planning Agent creates a structured 6-step plan."""
    assert planner_agent.validate_identifier_format("STU1001") is True
    assert planner_agent.validate_identifier_format("INVALID123") is False

    plan = planner_agent.create_execution_plan("STU1001", "Early warning screening")
    assert plan["student_id"] == "STU1001"
    assert plan["total_steps"] == 6
    assert len(plan["steps"]) == 6
    step_ids = [s["step_id"] for s in plan["steps"]]
    assert "STEP_DATA_RETRIEVAL" in step_ids
    assert "STEP_CRITIC_VALIDATION" in step_ids


def test_analytics_agent_analysis():
    """Verify that Analytics Agent retrieves records via MCP and computes indicators."""
    res = analytics_agent.analyze_student("STU1001")
    assert res["success"] is True
    assert "attendance" in res["indicators"]
    assert "assessments" in res["indicators"]
    assert "assignments" in res["indicators"]
    assert isinstance(res["concerns"], list)
    assert res["student_id"] == "STU1001"


def test_intervention_agent_recommendations():
    """Verify that Intervention Agent maps concerns to actionable, structured plans."""
    sample_concerns = [
        {
            "concern_type": "ATTENDANCE_LOW",
            "subject_id": "CS201",
            "severity": "HIGH",
            "evidence": "22/40 classes attended (55.0%)",
            "metric_value": 55.0,
        }
    ]
    interventions = intervention_agent.formulate_interventions(
        student_id="STU1016",
        concerns=sample_concerns,
        indicators={"attendance": {"overall_pct": 55.0}},
        support_priority="HIGH",
    )
    assert len(interventions) >= 1
    item = interventions[0]
    assert "concern" in item
    assert "recommended_action" in item
    assert "responsible_role" in item
    assert "suggested_review_period" in item
    assert "measurable_outcome" in item


def test_critic_agent_validation():
    """Verify that Critic Agent validates calculations and detects violations."""
    raw_attendance = data_service.get_attendance_history("STU1001")
    raw_assessments = data_service.get_assessment_results("STU1001")
    raw_assignments = data_service.get_assignment_status("STU1001")

    valid_res = critic_agent.validate_analysis(
        student_id="STU1001",
        indicators={"attendance": {}, "assessments": {}, "assignments": {}},
        concerns=[],
        interventions=[{
            "concern": "Satisfactory Progress",
            "concern_type": "GENERAL_MONITORING",
            "recommended_action": "Continue current routine",
            "responsible_role": "Faculty Mentor",
            "suggested_review_period": "End of Term",
            "measurable_outcome": "Maintain >=75% attendance",
        }],
        raw_attendance=raw_attendance,
        raw_assessments=raw_assessments,
        raw_assignments=raw_assignments,
    )
    assert valid_res["valid"] is True
    assert len(valid_res["errors"]) == 0
