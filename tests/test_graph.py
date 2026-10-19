"""Tests for LangGraph Orchestration and Conditional Routing."""

import pytest
from orchestration.graph import (
    edupilot_graph,
    initialize_state,
    run_student_analysis,
    run_batch_analysis,
)


def test_graph_structure():
    """Verify nodes exist in compiled LangGraph."""
    nodes = edupilot_graph.nodes
    expected_nodes = [
        "input_validation",
        "academic_planner",
        "student_analytics",
        "intervention_planner",
        "critic_validation",
        "correction_node",
        "report_generator",
    ]
    for n in expected_nodes:
        assert n in nodes


def test_successful_student_workflow():
    """Verify normal student traversal through LangGraph to VALIDATED status."""
    state = run_student_analysis("STU1001")
    assert state["status"] == "COMPLETED"
    assert state["final_report"]["final_status"] == "VALIDATED"
    assert state["validation_passed"] is True
    assert len(state["execution_trace"]) >= 5
    assert len(state["mcp_tool_calls"]) >= 1


def test_invalid_input_routing():
    """Verify that invalid student ID routes directly to report generation with VALIDATION_FAILED."""
    state = run_student_analysis("STU9999")
    assert state["final_report"]["final_status"] == "VALIDATION_FAILED"
    assert len(state["errors"]) > 0
    # Steps should be limited (validation -> report)
    node_names = [step["node_name"] for step in state["execution_trace"]]
    assert "Input Validation" in node_names
    assert "Report Generator" in node_names
    assert "Academic Planning Agent" not in node_names


def test_batch_analysis():
    """Verify batch workflow execution across multiple student IDs."""
    batch_ids = ["STU1001", "STU1016", "STU1026"]
    results = run_batch_analysis(batch_ids)
    assert len(results) == 3
    for r in results:
        assert r["status"] == "COMPLETED"
        assert r["final_report"]["student_id"] in batch_ids
