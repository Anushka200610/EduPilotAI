"""Shared State for EduPilot AI LangGraph Orchestrator.

Defines the typed dictionary containing the complete academic review context,
execution plan, evidence logs, indicators, critic validation results,
audit trace, and final report.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class EduPilotState(TypedDict):
    """Complete typed state passed between LangGraph nodes."""

    # Request metadata
    request_id: str
    student_id: str
    batch_ids: Optional[List[str]]
    analysis_mode: str  # "single" or "batch"
    analysis_objective: str

    # Execution Plan (Planner Agent)
    execution_plan: Dict[str, Any]

    # Academic Data & Indicators (Analytics Agent via MCP)
    profile: Dict[str, Any]
    indicators: Dict[str, Any]
    concerns: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    support_priority: str

    # Interventions (Intervention Planning Agent)
    interventions: List[Dict[str, Any]]

    # Validation & Invariants (Critic Agent)
    validation_results: Dict[str, Any]
    validation_passed: bool
    retry_count: int
    max_retries: int

    # Observability & Traceability
    execution_trace: List[Dict[str, Any]]
    mcp_tool_calls: List[Dict[str, Any]]

    # Final Output
    final_report: Dict[str, Any]
    status: str  # "INITIALIZED", "RUNNING", "COMPLETED", "FAILED", "CORRECTION"
    errors: List[str]
