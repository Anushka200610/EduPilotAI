"""Local MCP Server for EduPilot AI.

Exposes standard Academic Analysis Tools conforming to the Model Context Protocol (MCP 2.x).
Can be run as a standalone stdio process or interfaced through the EduPilot MCP Client.

Registered Academic Tools:
1. get_student_profile(student_id: str)
2. get_attendance_history(student_id: str)
3. get_assessment_results(student_id: str)
4. get_assignment_status(student_id: str)
5. calculate_attendance(student_id: str)
6. calculate_academic_indicators(student_id: str)
7. validate_intervention_plan(student_id: str, intervention_plan_json: str, indicators_json: str)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.mcpserver import MCPServer
import tools.academic_tools as academic_tools


def create_mcp_server() -> MCPServer:
    """Instantiate and configure the EduPilot Academic MCP Server."""
    server = MCPServer("edupilot-academic-server")

    @server.tool()
    def get_student_profile(student_id: str) -> str:
        """Retrieve demographic and registration details for a student.

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.get_student_profile(student_id)
        return json.dumps(result)

    @server.tool()
    def get_attendance_history(student_id: str) -> str:
        """Retrieve subject-wise attendance logs and total held/attended classes.

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.get_attendance_history(student_id)
        return json.dumps(result)

    @server.tool()
    def get_assessment_results(student_id: str) -> str:
        """Retrieve all assessment entries (quizzes, mid-term, end-term) for a student.

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.get_assessment_results(student_id)
        return json.dumps(result)

    @server.tool()
    def get_assignment_status(student_id: str) -> str:
        """Retrieve assignment submissions and status (SUBMITTED, LATE, MISSING).

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.get_assignment_status(student_id)
        return json.dumps(result)

    @server.tool()
    def calculate_attendance(student_id: str) -> str:
        """Calculate attendance percentages and identify low attendance concerns (<75%).

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.calculate_attendance(student_id)
        return json.dumps(result)

    @server.tool()
    def calculate_academic_indicators(student_id: str) -> str:
        """Calculate composite academic indicators: attendance, marks, trends, and assignment status.

        Args:
            student_id: The unique student identifier (e.g., STU1001).
        """
        result = academic_tools.calculate_academic_indicators(student_id)
        return json.dumps(result)

    @server.tool()
    def validate_intervention_plan(
        student_id: str, intervention_plan_json: str, indicators_json: str
    ) -> str:
        """Validate proposed intervention recommendations against evidence and rule invariants.

        Args:
            student_id: The unique student identifier.
            intervention_plan_json: JSON string representing the list of intervention items.
            indicators_json: JSON string representing the calculated academic indicators.
        """
        try:
            plan = json.loads(intervention_plan_json)
        except Exception as e:
            return json.dumps({
                "valid": False,
                "errors": [f"Malformed intervention_plan_json: {str(e)}"],
                "warnings": [],
            })

        try:
            indicators = json.loads(indicators_json)
        except Exception as e:
            return json.dumps({
                "valid": False,
                "errors": [f"Malformed indicators_json: {str(e)}"],
                "warnings": [],
            })

        result = academic_tools.validate_intervention_plan(student_id, plan, indicators)
        return json.dumps(result)

    return server


# Global server instance
mcp_server = create_mcp_server()

if __name__ == "__main__":
    # Run standalone stdio server for MCP clients
    print("Starting EduPilot MCP Server on stdio transport...", file=sys.stderr)
    mcp_server.run(transport="stdio")
