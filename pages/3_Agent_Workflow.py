"""Page 3: Agent Workflow for EduPilot AI.

Displays the live execution trace from LangGraph node transitions,
explicit AI agent taxonomy classification (Goal-Based, Model-Based Reflex,
Utility-Based, Learning & Verification), interactive step inspector,
real MCP tool invocations, and execution latencies.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
from services.data_service import data_service
from services.agent_service import agent_service
from agents.planner_agent import planner_agent
from agents.analytics_agent import analytics_agent
from agents.intervention_agent import intervention_agent
from agents.critic_agent import critic_agent

st.set_page_config(page_title="Agent Workflow | EduPilot AI", page_icon="⚡", layout="wide")

st.title("⚡ Agent Workflow & LangGraph Execution Trace")
st.caption("Live observability into agent state transitions, Russell & Norvig agent taxonomy, MCP tool calls, and conditional routing")

# -----------------------------------------------------------------------------
# 1. AI Agent Taxonomy Badges (Russell & Norvig Framework)
# -----------------------------------------------------------------------------
st.markdown("### 🤖 Multi-Agent Taxonomy Classification (Russell & Norvig)")
tax_col1, tax_col2, tax_col3, tax_col4 = st.columns(4)

with tax_col1:
    st.markdown(
        """
        <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 12px; height: 100%;">
            <div style="font-size: 13px; font-weight: bold; color: #1E40AF;">AGENT 1</div>
            <div style="font-size: 15px; font-weight: bold; color: #1E3A8A; margin: 4px 0;">Academic Planner</div>
            <span style="background-color: #2563EB; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">🎯 Goal-Based Agent</span>
            <p style="font-size: 12px; color: #374151; margin-top: 8px;">
                Decomposes the high-level review goal into an ordered 6-step action plan and specifies required indicators.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col2:
    st.markdown(
        """
        <div style="background-color: #F0FDFA; border: 1px solid #99F6E4; border-radius: 8px; padding: 12px; height: 100%;">
            <div style="font-size: 13px; font-weight: bold; color: #0F766E;">AGENT 2</div>
            <div style="font-size: 15px; font-weight: bold; color: #115E59; margin: 4px 0;">Student Analytics</div>
            <span style="background-color: #0D9488; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">🔍 Model-Based Reflex</span>
            <p style="font-size: 12px; color: #374151; margin-top: 8px;">
                Maintains internal state of longitudinal records via MCP tools; triggers condition-action reflex rules.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col3:
    st.markdown(
        """
        <div style="background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 12px; height: 100%;">
            <div style="font-size: 13px; font-weight: bold; color: #B45309;">AGENT 3</div>
            <div style="font-size: 15px; font-weight: bold; color: #92400E; margin: 4px 0;">Intervention Planner</div>
            <span style="background-color: #D97706; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">⚖️ Utility-Based Agent</span>
            <p style="font-size: 12px; color: #374151; margin-top: 8px;">
                Maximizes pedagogical recovery utility function <em>U(Action, Severity, Role)</em> balancing impact vs student burden.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col4:
    st.markdown(
        """
        <div style="background-color: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 8px; padding: 12px; height: 100%;">
            <div style="font-size: 13px; font-weight: bold; color: #6B21A8;">AGENT 4</div>
            <div style="font-size: 15px; font-weight: bold; color: #581C87; margin: 4px 0;">Critic & Auditor</div>
            <span style="background-color: #7C3AED; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">🛡️ Learning & Verification</span>
            <p style="font-size: 12px; color: #374151; margin-top: 8px;">
                Acts as an adversarial critic asserting mathematical invariants; drives the correction feedback learning loop.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. Live State or Quick Run Trigger
# -----------------------------------------------------------------------------
state = st.session_state.get("latest_state")

# Quick Analysis Launcher bar
all_students = data_service.get_all_students()
student_ids = [s["student_id"] for s in all_students] if all_students else ["STU1016"]

with st.expander("🔄 Run Live Analysis or Select Another Student", expanded=(state is None)):
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        current_id = state.get("student_id", "STU1016") if state else "STU1016"
        def_idx = student_ids.index(current_id) if current_id in student_ids else 0
        target_student_id = st.selectbox("Select Student to Trace Execution", student_ids, index=def_idx)
    with col_btn:
        st.write("")
        st.write("")
        if st.button("⚡ Trace Agentic Workflow", use_container_width=True, type="primary"):
            with st.spinner(f"Orchestrating agents for {target_student_id}..."):
                new_state = agent_service.run_student_analysis(target_student_id)
                st.session_state["latest_state"] = new_state
                if "analysis_history" not in st.session_state:
                    st.session_state["analysis_history"] = []
                if new_state.get("report"):
                    st.session_state["analysis_history"].insert(0, new_state["report"])
                state = new_state
                st.rerun()

if not state:
    st.info("ℹ️ Please select a student above and click **⚡ Trace Agentic Workflow** to generate a live trace.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. Execution KPI Summary
# -----------------------------------------------------------------------------
student_id = state.get("student_id", "UNKNOWN")
trace = state.get("execution_trace", [])
mcp_calls = state.get("mcp_tool_calls", [])
plan = state.get("execution_plan", {})
retries = state.get("retry_count", 0)
total_ms = sum(t.get("duration_ms", 0.0) for t in trace)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Analyzed Student", student_id)
with k2:
    st.metric("Graph Nodes Executed", len(trace))
with k3:
    st.metric("MCP Tools Invoked", len(mcp_calls))
with k4:
    st.metric("Critic Retries", retries)
with k5:
    st.metric("Total Execution Latency", f"{total_ms:.1f} ms")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. Dynamic Visual Calling Flow
# -----------------------------------------------------------------------------
st.subheader("🔄 Dynamic Multi-Agent Calling Flow")
st.caption("Sequential node activations, state hand-offs, and tool invocations recorded during runtime")

# Create a visual breadcrumb / pipeline
flow_html = """
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 15px 0;">
"""
for idx, step in enumerate(trace):
    node_name = step.get("node_name", "Unknown")
    agent_type = step.get("agent_type", "System")
    duration = step.get("duration_ms", 0.0)
    status = step.get("status", "SUCCESS")
    
    # Choose color based on agent type
    if "Goal" in agent_type:
        bg_col = "#2563EB"
    elif "Reflex" in agent_type:
        bg_col = "#0D9488"
    elif "Utility" in agent_type:
        bg_col = "#D97706"
    elif "Learning" in agent_type or "Critic" in agent_type:
        bg_col = "#7C3AED"
    elif "Gateway" in agent_type:
        bg_col = "#475569"
    else:
        bg_col = "#16A34A"
        
    badge_html = f"""
    <div style="background-color: {bg_col}; color: white; padding: 8px 14px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;">
        <div style="font-size: 11px; opacity: 0.9; text-transform: uppercase;">Step {step.get('step_number', idx+1)}</div>
        <div style="font-weight: bold; font-size: 13px;">{node_name}</div>
        <div style="font-size: 10px; background: rgba(255,255,255,0.2); padding: 1px 6px; border-radius: 4px; margin-top: 4px;">{agent_type}</div>
        <div style="font-size: 10px; margin-top: 2px;">{duration:.1f} ms • {status}</div>
    </div>
    """
    flow_html += badge_html
    if idx < len(trace) - 1:
        flow_html += """<div style="font-size: 18px; color: #94A3B8; font-weight: bold;">➔</div>"""

flow_html += "</div>"
st.markdown(flow_html, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. Interactive Step Inspector (Dynamic Deep-Dive)
# -----------------------------------------------------------------------------
st.subheader("🔬 Interactive Execution Step Inspector")
st.caption("Inspect input percepts, internal reasoning, decision rules, and output state for each agent invocation")

step_options = [
    f"Step {t.get('step_number')}: {t.get('node_name')} ({t.get('agent_type')})"
    for t in trace
]

if step_options:
    selected_step_str = st.selectbox("Select Execution Step to Inspect", step_options, index=1 if len(step_options) > 1 else 0)
    selected_idx = step_options.index(selected_step_str)
    selected_trace = trace[selected_idx]

    # Taxonomy profiles mapping
    agent_profiles = {
        "Academic Planning Agent": {
            "type": "Goal-Based Agent",
            "formal_class": "Goal-Based Agent (Russell & Norvig, Ch. 2)",
            "peas": {
                "Performance Measure": "Plan completeness, logical indicator dependency ordering, execution feasibility",
                "Environment": "Academic request context, student registry, target term",
                "Actuators": "Typed 6-step execution plan written to EduPilotState['execution_plan']",
                "Sensors": "Student ID format string, analysis objective specification",
            },
            "theory": "A Goal-Based Agent combines goal descriptions with information regarding the results of possible actions to choose actions that achieve the objective. Here, the agent receives the goal 'Comprehensive Academic Review' and generates an ordered multi-step plan decomposing the required indicators.",
        },
        "Student Analytics Agent": {
            "type": "Model-Based Reflex Agent",
            "formal_class": "Model-Based Reflex Agent with Internal State (Russell & Norvig, Ch. 2)",
            "peas": {
                "Performance Measure": "Accuracy of computed indicators, zero ungrounded findings, precision of evidence",
                "Environment": "Synthetic academic records (attendance, assessments, assignments via MCP tools)",
                "Actuators": "State updates: indicators dictionary, flagged concerns, traceable evidence items",
                "Sensors": "MCP tool returns: JSON payloads from get_attendance_history, get_assessment_results, etc.",
            },
            "theory": "A Model-Based Reflex Agent maintains an internal state reflecting how the world evolves (e.g. tracking historical scores across sequential assessments) and evaluates condition-action rules (e.g. IF attendance < 75% THEN flag ATTENDANCE_LOW).",
        },
        "Intervention Planning Agent": {
            "type": "Utility-Based Agent",
            "formal_class": "Utility-Based Agent (Russell & Norvig, Ch. 2)",
            "peas": {
                "Performance Measure": "Expected academic recovery utility, pedagogical feasibility, faculty role appropriateness",
                "Environment": "Flagged concerns, traceable evidence items, faculty role taxonomy",
                "Actuators": "Prioritized intervention roadmaps with roles, review periods (1-4 wks), measurable outcomes",
                "Sensors": "Identified concerns list and quantitative evidence from Analytics Agent",
            },
            "theory": "A Utility-Based Agent uses a utility function to map states to real numbers, quantifying the desirability of outcomes. In EduPilot AI, it optimizes U(Action, Severity, Role) to balance support intensity against student and faculty burden.",
        },
        "Critic & Validation Agent": {
            "type": "Learning & Verification Agent",
            "formal_class": "Learning & Verification Agent with Critic Component (Russell & Norvig, Ch. 2)",
            "peas": {
                "Performance Measure": "Adversarial detection of invariant violations, mathematical precision, verification soundness",
                "Environment": "Emitted indicators, evidence claims, intervention plans, ground truth datasets",
                "Actuators": "Validation status flag, discrepancy error list, routing signal to correction node",
                "Sensors": "Recomputed calculations, raw data re-queries, invariant assertions",
            },
            "theory": "A Learning Agent features a Critic element that evaluates agent behavior against external performance standards (invariants). If discrepancies are detected, it generates learning/error feedback that triggers the Correction Node for bounded retries.",
        },
        "Input Validation": {
            "type": "Deterministic Gateway",
            "formal_class": "Simple Reflex Invariant Gateway",
            "peas": {
                "Performance Measure": "Filtering invalid formats before downstream computation",
                "Environment": "Student registry database",
                "Actuators": "Routing decision: valid -> planner, invalid -> bypass to report",
                "Sensors": "Regex string match & existence check",
            },
            "theory": "Deterministic verification guardrail enforcing domain boundary conditions.",
        },
        "Report Generator": {
            "type": "Completion Node",
            "formal_class": "Deterministic Synthesis Node",
            "peas": {
                "Performance Measure": "18-field schema adherence, audit readiness",
                "Environment": "Complete EduPilotState",
                "Actuators": "Standardized academic intervention report JSON/PDF",
                "Sensors": "All upstream state artifacts",
            },
            "theory": "Generates immutable 18-field academic report for human faculty review.",
        },
    }

    current_node = selected_trace.get("node_name", "")
    profile = agent_profiles.get(current_node, {
        "type": selected_trace.get("agent_type", "System Node"),
        "formal_class": "LangGraph Orchestration Node",
        "peas": {
            "Performance Measure": "Correct state transition",
            "Environment": "Shared LangGraph state",
            "Actuators": "State update",
            "Sensors": "Upstream node state",
        },
        "theory": "Executes state transition within the LangGraph state machine.",
    })

    insp_c1, insp_c2 = st.columns([1, 1])

    with insp_c1:
        st.markdown(f"#### 🏷️ Agent Taxonomy & Theoretical Profile")
        st.markdown(f"**Node Name**: `{current_node}`")
        st.markdown(f"**Agent Taxonomy**: `{profile['type']}`")
        st.markdown(f"**Theoretical Foundation**: {profile['formal_class']}")
        st.info(f"💡 **AI Theory**: {profile['theory']}")

        st.markdown("**PEAS Framework Specification**:")
        peas_df = pd.DataFrame([
            {"PEAS Dimension": k, "Specification": v}
            for k, v in profile["peas"].items()
        ])
        st.dataframe(peas_df, use_container_width=True, hide_index=True)

    with insp_c2:
        st.markdown(f"#### ⚙️ Execution State & Telemetry")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Step Number", selected_trace.get("step_number"))
        with m_col2:
            st.metric("Latency", f"{selected_trace.get('duration_ms', 0.0):.2f} ms")
        with m_col3:
            st.metric("Status", selected_trace.get("status"))

        st.markdown(f"**Summary**: {selected_trace.get('summary')}")
        st.markdown(f"**Timestamp**: `{selected_trace.get('timestamp')}`")

        # Specific Node Details Viewer
        if current_node == "Academic Planning Agent":
            st.markdown("📋 **Formulated 6-Step Plan**:")
            plan_steps = plan.get("steps", [])
            for ps in plan_steps:
                st.markdown(f"- **Step {ps.get('step_index')}**: {ps.get('name')} (`{ps.get('agent_type')}`) → Expected: *{ps.get('expected_output')}*")
        elif current_node == "Student Analytics Agent":
            st.markdown("📊 **Emitted Indicators & Concerns**:")
            ind = state.get("indicators", {})
            st.json({
                "overall_attendance_pct": ind.get("attendance", {}).get("overall_pct"),
                "assessment_average_pct": ind.get("assessments", {}).get("overall_average_pct"),
                "assignment_completion_pct": ind.get("assignments", {}).get("completion_pct"),
                "flagged_concerns": state.get("concerns", []),
            })
        elif current_node == "Intervention Planning Agent":
            st.markdown("⚖️ **Utility Optimization Result**:")
            intervs = state.get("interventions", [])
            for iv in intervs:
                st.markdown(f"- **{iv.get('concern_type')}** ({iv.get('priority')} Priority) → Action: {iv.get('recommended_action')} (Assigned: *{iv.get('responsible_role')}*)")
        elif current_node == "Critic & Validation Agent":
            st.markdown("🛡️ **Critic Invariant Audit Checks**:")
            critic_res = state.get("validation_results", {})
            st.json({
                "valid": critic_res.get("valid"),
                "passed_checks": critic_res.get("passed_checks"),
                "discrepancies": critic_res.get("discrepancies", []),
                "checks": critic_res.get("checks", {}),
            })
        else:
            if selected_trace.get("details"):
                st.json(selected_trace.get("details"))

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. Ordered Node Execution Trace Table & Latency Breakdown
# -----------------------------------------------------------------------------
st.subheader("📜 Step-by-Step LangGraph Node Execution Trace")
if trace:
    df_trace = pd.DataFrame([
        {
            "Step": t.get("step_number"),
            "Node / Agent": t.get("node_name"),
            "AI Agent Type": t.get("agent_type", "System"),
            "Status": t.get("status"),
            "Duration (ms)": t.get("duration_ms"),
            "Summary": t.get("summary"),
            "Timestamp": t.get("timestamp"),
        }
        for t in trace
    ])
    st.dataframe(df_trace, use_container_width=True, hide_index=True)

    fig_latency = px.bar(
        df_trace,
        x="Duration (ms)",
        y="Node / Agent",
        orientation="h",
        color="AI Agent Type",
        title="Execution Latency per Graph Node by AI Agent Type (ms)",
        text="Duration (ms)",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_latency.update_layout(height=300)
    st.plotly_chart(fig_latency, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. MCP Tool Invocations Table
# -----------------------------------------------------------------------------
st.subheader(f"🛠️ Real MCP Tool Invocations ({len(mcp_calls)})")
st.markdown(
    "Standardized tools executed through the Model Context Protocol (`MCPServer` in `mcp_server/server.py`):"
)

if mcp_calls:
    df_mcp = pd.DataFrame([
        {
            "Call ID": c.get("call_id"),
            "Tool Name": c.get("tool_name"),
            "Status": c.get("status"),
            "Latency (ms)": c.get("duration_ms"),
            "Summary": c.get("summary"),
            "Arguments": json.dumps(c.get("arguments", {})),
            "Timestamp": c.get("timestamp"),
        }
        for c in mcp_calls
    ])
    st.dataframe(df_mcp, use_container_width=True, hide_index=True)
else:
    st.info("No MCP tool calls logged in current state.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. Complete Orchestration Graph Structure
# -----------------------------------------------------------------------------
st.subheader("🗺️ Orchestration Graph State Machine")
st.markdown(
    """
    ```mermaid
    graph LR
        START([START]) --> Val[1. Input Validation<br/><i>Gateway</i>]
        Val -->|Valid| Plan[2. Academic Planner<br/><b>Goal-Based Agent</b>]
        Val -->|Invalid| Rpt[7. Report Generator<br/><i>Completion</i>]
        Plan --> Analytics[3. Student Analytics<br/><b>Model-Based Reflex Agent</b>]
        Analytics <-->|MCP Call| MCP[(Academic MCP Server)]
        Analytics --> Interv[4. Intervention Planner<br/><b>Utility-Based Agent</b>]
        Interv --> Critic[5. Critic Validation<br/><b>Learning & Audit Agent</b>]
        Critic -->|Passed| Rpt
        Critic -->|Discrepancy & Retry < 2| Corr[6. Correction Node<br/><i>Learning Feedback</i>]
        Corr --> Analytics
        Rpt --> END([END])

        classDef active fill:#2563EB,stroke:#1D4ED8,stroke-width:2px,color:white;
        classDef reflex fill:#0D9488,stroke:#0F766E,stroke-width:2px,color:white;
        classDef utility fill:#D97706,stroke:#B45309,stroke-width:2px,color:white;
        classDef critic fill:#7C3AED,stroke:#6B21A8,stroke-width:2px,color:white;

        class Plan active;
        class Analytics reflex;
        class Interv utility;
        class Critic critic;
    ```
    """
)
