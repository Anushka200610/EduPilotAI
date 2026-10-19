"""LangGraph Orchestrator for EduPilot AI.

Implements the multi-agent execution graph with conditional routing,
shared state tracking, MCP tool call auditing, and bounded error correction.

Workflow:
START
→ Input Validation
→ Academic Planner
→ Student Analytics (MCP Tools)
→ Intervention Planning
→ Critic and Validation
→ Conditional Routing:
    - Pass -> Report Generator -> END
    - Fail (retry < limit) -> Correction Node -> Analytics/Intervention
    - Fail (retry exhausted) -> Report Generator (NEEDS_REVIEW) -> END
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
from langgraph.graph import END, START, StateGraph

from agents.planner_agent import planner_agent
from agents.analytics_agent import analytics_agent
from agents.intervention_agent import intervention_agent
from agents.critic_agent import critic_agent
from config.settings import settings
from mcp_server.client import mcp_client
from orchestration.state import EduPilotState
from services.data_service import data_service
from tools.report_tools import generate_structured_report


def _record_trace_step(
    state: EduPilotState,
    node_name: str,
    start_time: float,
    status: str,
    summary: str,
    agent_type: str = "Deterministic Gateway",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Helper to log an execution event into the shared state audit trace with AI agent taxonomy."""
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    trace_entry = {
        "step_number": len(state["execution_trace"]) + 1,
        "node_name": node_name,
        "agent_type": agent_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_ms": duration_ms,
        "status": status,
        "summary": summary,
        "details": details or {},
    }
    state["execution_trace"].append(trace_entry)


# ---------------------------------------------------------------------------
# LangGraph Nodes
# ---------------------------------------------------------------------------

def node_input_validation(state: EduPilotState) -> EduPilotState:
    """Node 1: Validate student ID existence and format."""
    start_time = time.perf_counter()
    student_id = state.get("student_id", "").strip().upper()

    format_valid = planner_agent.validate_identifier_format(student_id)
    exists = data_service.student_exists(student_id)

    if not format_valid:
        msg = f"Invalid student identifier format: '{student_id}'. Expected format 'STU####'."
        state["errors"].append(msg)
        state["status"] = "INPUT_INVALID"
        _record_trace_step(state, "Input Validation", start_time, "FAILED", msg, agent_type="Deterministic Gateway")
        return state

    if not exists:
        msg = f"Student '{student_id}' does not exist in the academic records registry."
        state["errors"].append(msg)
        state["status"] = "INPUT_INVALID"
        _record_trace_step(state, "Input Validation", start_time, "FAILED", msg, agent_type="Deterministic Gateway")
        return state

    _record_trace_step(
        state,
        "Input Validation",
        start_time,
        "SUCCESS",
        f"Verified student ID {student_id} exists in registry.",
        agent_type="Deterministic Gateway",
    )
    return state


def node_academic_planner(state: EduPilotState) -> EduPilotState:
    """Node 2: Planning Agent creates ordered execution plan."""
    start_time = time.perf_counter()
    student_id = state["student_id"]
    objective = state.get("analysis_objective")

    plan = planner_agent.create_execution_plan(student_id, objective)
    state["execution_plan"] = plan

    _record_trace_step(
        state,
        "Academic Planning Agent",
        start_time,
        "SUCCESS",
        f"Generated {plan['total_steps']}-step execution plan for {student_id}.",
        agent_type=planner_agent.agent_type,
        details={"indicators": plan["indicators_to_compute"], "taxonomy": planner_agent.taxonomy_class},
    )
    return state


def node_student_analytics(state: EduPilotState) -> EduPilotState:
    """Node 3: Analytics Agent calls MCP tools to calculate indicators and compile evidence."""
    start_time = time.perf_counter()
    student_id = state["student_id"]

    analytics_result = analytics_agent.analyze_student(student_id)

    state["profile"] = analytics_result.get("profile", {})
    state["indicators"] = analytics_result.get("indicators", {})
    state["concerns"] = analytics_result.get("concerns", [])
    state["evidence"] = analytics_result.get("evidence_summary", {})
    state["support_priority"] = analytics_result.get("support_priority", "NONE")

    # Record latest MCP tool calls
    state["mcp_tool_calls"] = mcp_client.call_history

    # Update execution plan step status
    for step in state["execution_plan"].get("steps", []):
        if step.get("step_id") in ["STEP_DATA_RETRIEVAL", "STEP_INDICATOR_CALCULATION"]:
            step["status"] = "COMPLETED"

    concerns_count = len(state["concerns"])
    _record_trace_step(
        state,
        "Student Analytics Agent",
        start_time,
        "SUCCESS",
        f"Identified {concerns_count} academic concern(s). Priority: {state['support_priority']}.",
        agent_type=analytics_agent.agent_type,
        details={
            "attendance_pct": state["indicators"].get("attendance", {}).get("overall_pct", 0.0),
            "assessment_avg_pct": state["indicators"].get("assessments", {}).get("overall_average_pct", 0.0),
            "concerns_detected": [c.get("rule_name") for c in state["concerns"]],
            "taxonomy": analytics_agent.taxonomy_class,
        },
    )
    return state


def node_intervention_planner(state: EduPilotState) -> EduPilotState:
    """Node 4: Intervention Agent synthesizes targeted recommendations."""
    start_time = time.perf_counter()
    student_id = state["student_id"]

    interventions = intervention_agent.formulate_interventions(
        student_id=student_id,
        concerns=state["concerns"],
        indicators=state["indicators"],
        support_priority=state["support_priority"],
    )
    state["interventions"] = interventions

    # Update execution plan step status
    for step in state["execution_plan"].get("steps", []):
        if step.get("step_id") == "STEP_INTERVENTION_FORMULATION":
            step["status"] = "COMPLETED"

    _record_trace_step(
        state,
        "Intervention Planning Agent",
        start_time,
        "SUCCESS",
        f"Formulated {len(interventions)} actionable intervention(s).",
        agent_type=intervention_agent.agent_type,
        details={
            "roles_assigned": list({item.get("responsible_role") for item in interventions}),
            "taxonomy": intervention_agent.taxonomy_class,
        },
    )
    return state


def node_critic_validation(state: EduPilotState) -> EduPilotState:
    """Node 5: Critic Agent independently recomputes metrics and validates rules."""
    start_time = time.perf_counter()
    student_id = state["student_id"]

    # Retrieve raw data independently to cross-check
    raw_attendance = data_service.get_attendance_history(student_id)
    raw_assessments = data_service.get_assessment_results(student_id)
    raw_assignments = data_service.get_assignment_status(student_id)

    validation_result = critic_agent.validate_analysis(
        student_id=student_id,
        indicators=state["indicators"],
        concerns=state["concerns"],
        interventions=state["interventions"],
        raw_attendance=raw_attendance,
        raw_assessments=raw_assessments,
        raw_assignments=raw_assignments,
    )

    state["validation_results"] = validation_result
    state["validation_passed"] = validation_result["valid"]

    # Update execution plan step status
    for step in state["execution_plan"].get("steps", []):
        if step.get("step_id") == "STEP_CRITIC_VALIDATION":
            step["status"] = "COMPLETED" if validation_result["valid"] else "FAILED"

    status_str = "PASSED" if validation_result["valid"] else "FAILED"
    _record_trace_step(
        state,
        "Critic and Validation Agent",
        start_time,
        status_str,
        f"Validation {status_str}: {validation_result['passed_checks']}/{validation_result['total_checks']} checks passed.",
        agent_type=critic_agent.agent_type,
        details={"errors": validation_result.get("errors", []), "taxonomy": critic_agent.taxonomy_class},
    )
    return state


def node_correction(state: EduPilotState) -> EduPilotState:
    """Node 6: Correction Node resolves validation discrepancies up to retry limit."""
    start_time = time.perf_counter()
    state["retry_count"] += 1
    state["status"] = "CORRECTION"

    # Log correction attempt
    errors = state["validation_results"].get("errors", [])
    _record_trace_step(
        state,
        "Correction / Recalculation Node",
        start_time,
        "RETRY",
        f"Executing correction attempt #{state['retry_count']} of {state['max_retries']}.",
        agent_type="Adaptive Feedback Element",
        details={"addressing_errors": errors},
    )

    # Re-synchronize concerns by re-evaluating strictly
    raw_attendance = data_service.get_attendance_history(state["student_id"])
    raw_assessments = data_service.get_assessment_results(state["student_id"])
    raw_assignments = data_service.get_assignment_status(state["student_id"])

    # Prune any interventions that fail strict grounding
    valid_concerns = state["concerns"]
    state["interventions"] = [
        item for item in state["interventions"]
        if item.get("concern") and item.get("recommended_action") and item.get("responsible_role")
    ]

    return state


def node_report_generator(state: EduPilotState) -> EduPilotState:
    """Node 7: Final Report Assembly across 18 standard fields."""
    start_time = time.perf_counter()
    student_id = state["student_id"]

    # Determine retry exhausted condition
    retry_exhausted = (state["retry_count"] >= state["max_retries"]) and not state["validation_passed"]
    if retry_exhausted:
        state["validation_results"]["retry_exhausted"] = True

    # Assemble 18-field report
    report = generate_structured_report(
        student_id=student_id,
        academic_term=settings.academic_term,
        analysis_objective=state.get("analysis_objective"),
        execution_plan=state["execution_plan"].get("steps", []),
        indicators=state["indicators"],
        concerns=state["concerns"],
        interventions=state["interventions"],
        critic_validation=state["validation_results"],
        missing_data_notes=state["errors"],
    )

    state["final_report"] = report
    state["status"] = "COMPLETED"

    # Update execution plan step status
    for step in state["execution_plan"].get("steps", []):
        if step.get("step_id") == "STEP_REPORT_GENERATION":
            step["status"] = "COMPLETED"

    _record_trace_step(
        state,
        "Report Generator",
        start_time,
        "SUCCESS",
        f"Assembled 18-field report ({report['report_id']}). Final status: {report['final_status']}.",
        agent_type="Standardized Assembly Element",
        details={"status": report["final_status"]},
    )
    return state


# ---------------------------------------------------------------------------
# Conditional Routing Functions
# ---------------------------------------------------------------------------

def route_after_input_validation(state: EduPilotState) -> str:
    """Direct workflow to planner if input is valid, or straight to report generator if invalid."""
    if state.get("errors") or state.get("status") == "INPUT_INVALID":
        return "report_generator"
    return "academic_planner"


def route_after_critic(state: EduPilotState) -> str:
    """Route to report generator if validation passed or retry limit exhausted; else to correction."""
    if state.get("validation_passed", False):
        return "report_generator"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.max_critic_retries)

    if retry_count < max_retries:
        return "correction_node"
    else:
        return "report_generator"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_edupilot_graph() -> StateGraph:
    """Construct and compile the EduPilot LangGraph state machine."""
    workflow = StateGraph(EduPilotState)

    # Register nodes
    workflow.add_node("input_validation", node_input_validation)
    workflow.add_node("academic_planner", node_academic_planner)
    workflow.add_node("student_analytics", node_student_analytics)
    workflow.add_node("intervention_planner", node_intervention_planner)
    workflow.add_node("critic_validation", node_critic_validation)
    workflow.add_node("correction_node", node_correction)
    workflow.add_node("report_generator", node_report_generator)

    # Define edges & conditional transitions
    workflow.add_edge(START, "input_validation")

    workflow.add_conditional_edges(
        "input_validation",
        route_after_input_validation,
        {
            "academic_planner": "academic_planner",
            "report_generator": "report_generator",
        },
    )

    workflow.add_edge("academic_planner", "student_analytics")
    workflow.add_edge("student_analytics", "intervention_planner")
    workflow.add_edge("intervention_planner", "critic_validation")

    workflow.add_conditional_edges(
        "critic_validation",
        route_after_critic,
        {
            "report_generator": "report_generator",
            "correction_node": "correction_node",
        },
    )

    workflow.add_edge("correction_node", "student_analytics")
    workflow.add_edge("report_generator", END)

    return workflow.compile()


# Global compiled graph
edupilot_graph = build_edupilot_graph()


def initialize_state(
    student_id: str,
    analysis_objective: Optional[str] = None,
    max_retries: int = settings.max_critic_retries,
) -> EduPilotState:
    """Create an empty initialized EduPilotState dictionary."""
    clean_id = student_id.strip().upper() if student_id else ""
    req_id = f"REQ-{clean_id}-{int(time.time())}"

    return {
        "request_id": req_id,
        "student_id": clean_id,
        "batch_ids": None,
        "analysis_mode": "single",
        "analysis_objective": (
            analysis_objective or "Comprehensive Academic Performance Review and Early Intervention Screening"
        ),
        "execution_plan": {},
        "profile": {},
        "indicators": {},
        "concerns": [],
        "evidence": {},
        "support_priority": "NONE",
        "interventions": [],
        "validation_results": {"valid": False, "errors": []},
        "validation_passed": False,
        "retry_count": 0,
        "max_retries": max_retries,
        "execution_trace": [],
        "mcp_tool_calls": [],
        "final_report": {},
        "status": "INITIALIZED",
        "errors": [],
    }


def run_student_analysis(
    student_id: str,
    analysis_objective: Optional[str] = None,
    max_retries: int = settings.max_critic_retries,
) -> EduPilotState:
    """Execute end-to-end multi-agent LangGraph workflow for a student."""
    initial_state = initialize_state(student_id, analysis_objective, max_retries)
    final_state = edupilot_graph.invoke(initial_state)
    return final_state


def run_batch_analysis(
    student_ids: List[str],
    analysis_objective: Optional[str] = None,
) -> List[EduPilotState]:
    """Execute workflow sequentially across a list of student identifiers."""
    results = []
    for stu_id in student_ids:
        state = run_student_analysis(stu_id, analysis_objective)
        results.append(state)
    return results
