"""MCP Client for EduPilot AI.

Provides standard interface for agent nodes to invoke academic tools through
the local MCP server. Logs all tool invocations, parameters, latencies,
statuses, and summaries for execution traceability.
"""

import asyncio
from datetime import datetime, timezone
import json
import time
from typing import Any, Dict, List, Optional

from mcp_server.server import mcp_server


class EduPilotMCPClient:
    """Client for invoking MCP Academic Tools with detailed audit tracing."""

    def __init__(self):
        self.server = mcp_server
        self._tool_call_history: List[Dict[str, Any]] = []

    def clear_history(self):
        """Reset the tool invocation history."""
        self._tool_call_history.clear()

    @property
    def call_history(self) -> List[Dict[str, Any]]:
        """Return the immutable audit log of all tool invocations."""
        return list(self._tool_call_history)

    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool asynchronously and record telemetry."""
        start_time = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()
        call_id = f"mcp-call-{len(self._tool_call_history) + 1:04d}"

        try:
            # Make the real MCP tool call through the MCPServer
            res = await self.server.call_tool(tool_name, arguments)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Parse content from MCP TextContent
            if res.content and len(res.content) > 0:
                raw_text = res.content[0].text
                try:
                    parsed_result = json.loads(raw_text)
                except Exception:
                    parsed_result = {"raw_text": raw_text}
            else:
                parsed_result = {"status": "empty_response"}

            # Generate concise summary
            if isinstance(parsed_result, dict):
                summary = (
                    f"Success: {parsed_result.get('count', 'ok')}"
                    if parsed_result.get("success", True)
                    else f"Error: {parsed_result.get('error', 'failed')}"
                )
            else:
                summary = "Completed"

            log_entry = {
                "call_id": call_id,
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": timestamp,
                "duration_ms": duration_ms,
                "status": "SUCCESS" if not res.is_error else "ERROR",
                "summary": summary,
                "result_preview": str(parsed_result)[:180] + "..." if len(str(parsed_result)) > 180 else str(parsed_result),
            }
            self._tool_call_history.append(log_entry)
            return parsed_result

        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_entry = {
                "call_id": call_id,
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": timestamp,
                "duration_ms": duration_ms,
                "status": "ERROR",
                "summary": f"Exception: {str(e)}",
                "result_preview": f"Failed with exception: {str(e)}",
            }
            self._tool_call_history.append(log_entry)
            return {"success": False, "error": str(e), "tool_name": tool_name}

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper to execute an MCP tool."""
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.call_tool_async(tool_name, arguments)).result()
        except RuntimeError:
            # No active running loop in current thread
            return asyncio.run(self.call_tool_async(tool_name, arguments))

    # High-level convenience wrappers
    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("get_student_profile", {"student_id": student_id})

    def get_attendance_history(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("get_attendance_history", {"student_id": student_id})

    def get_assessment_results(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("get_assessment_results", {"student_id": student_id})

    def get_assignment_status(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("get_assignment_status", {"student_id": student_id})

    def calculate_attendance(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("calculate_attendance", {"student_id": student_id})

    def calculate_academic_indicators(self, student_id: str) -> Dict[str, Any]:
        return self.call_tool("calculate_academic_indicators", {"student_id": student_id})

    def validate_intervention_plan(
        self, student_id: str, intervention_plan: List[Dict[str, Any]], indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self.call_tool(
            "validate_intervention_plan",
            {
                "student_id": student_id,
                "intervention_plan_json": json.dumps(intervention_plan),
                "indicators_json": json.dumps(indicators),
            },
        )


# Global singleton client instance
mcp_client = EduPilotMCPClient()
