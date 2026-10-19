import asyncio
import pytest
from mcp_server.server import mcp_server
from mcp_server.client import mcp_client


def test_mcp_server_tool_listing():
    """Verify that all 7 academic tools are registered on the MCP server."""
    tools = asyncio.run(mcp_server.list_tools())
    tool_names = [t.name for t in tools]

    expected = [
        "get_student_profile",
        "get_attendance_history",
        "get_assessment_results",
        "get_assignment_status",
        "calculate_attendance",
        "calculate_academic_indicators",
        "validate_intervention_plan",
    ]
    for exp in expected:
        assert exp in tool_names


def test_mcp_client_tool_invocations():
    """Verify tool invocation, response parsing, and telemetry logging."""
    mcp_client.clear_history()

    # Call profile
    res1 = mcp_client.get_student_profile("STU1001")
    assert res1["success"] is True
    assert res1["student_id"] == "STU1001"

    # Call attendance
    res2 = mcp_client.calculate_attendance("STU1001")
    assert res2["success"] is True
    assert "overall_attendance_pct" in res2

    # Check telemetry history
    history = mcp_client.call_history
    assert len(history) == 2
    assert history[0]["tool_name"] == "get_student_profile"
    assert history[0]["status"] == "SUCCESS"
    assert history[1]["tool_name"] == "calculate_attendance"
    assert history[1]["status"] == "SUCCESS"


def test_mcp_client_invalid_student():
    """Verify proper error handling when tool called with unknown student ID."""
    res = mcp_client.get_student_profile("STU_UNKNOWN")
    assert res["success"] is False
    assert "error" in res
