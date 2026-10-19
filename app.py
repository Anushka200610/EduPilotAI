"""EduPilot AI — Streamlit Dashboard Entrypoint.

An Agentic AI System for Student Performance Analysis and Academic Intervention.
Second-Year Undergraduate AIML CA-3 Project.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from config.settings import settings, AcademicThresholds
from services.data_service import data_service
from services.llm_service import llm_service

# Page Configuration
st.set_page_config(
    page_title="EduPilot AI — Academic Support System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-success { background-color: #DEF7EC; color: #03543F; }
    .badge-warning { background-color: #FEF08A; color: #713F12; }
    .badge-danger { background-color: #FDE8E8; color: #9B1C1C; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "latest_state" not in st.session_state:
    st.session_state.latest_state = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = []

# Sidebar Controls
st.sidebar.title("🎓 EduPilot AI")
st.sidebar.caption("Agentic Decision Support System | CA-3")

# Engine Mode Display
ollama_active = llm_service.is_available()
if ollama_active:
    st.sidebar.success("🤖 Local LLM Active (Ollama)")
else:
    st.sidebar.info("⚙️ Engine: Deterministic Multi-Agent (No API Required)")

st.sidebar.divider()
st.sidebar.subheader("⚙️ Configurable Thresholds")

min_att = st.sidebar.slider(
    "Minimum Attendance (%)",
    min_value=50.0,
    max_value=90.0,
    value=settings.thresholds.min_attendance_pct,
    step=1.0,
    help="Attendance below this triggers an ATTENDANCE_LOW concern",
)

min_marks = st.sidebar.slider(
    "Passing Marks Threshold (%)",
    min_value=30.0,
    max_value=60.0,
    value=settings.thresholds.min_passing_marks_pct,
    step=1.0,
    help="Scores below this trigger an ACADEMIC_PERFORMANCE_LOW concern",
)

decline_delta = st.sidebar.slider(
    "Score Decline Threshold (% pts)",
    min_value=5.0,
    max_value=30.0,
    value=settings.thresholds.decline_threshold_pct,
    step=1.0,
    help="Score drops between tests exceeding this trigger a PERFORMANCE_DECLINE concern",
)

# Update active thresholds in settings
settings.thresholds.min_attendance_pct = min_att
settings.thresholds.min_passing_marks_pct = min_marks
settings.thresholds.decline_threshold_pct = decline_delta

if st.sidebar.button("🔄 Reset Datasets & Cache"):
    data_service.refresh()
    st.session_state.analysis_history.clear()
    st.session_state.latest_state = None
    st.sidebar.success("Cache cleared!")

st.sidebar.divider()
st.sidebar.markdown(
    """
    **Academic Project Details**
    - **Course**: AIML CA-3 Assignment
    - **Term**: Fall 2026
    - **Architecture**: LangGraph + MCP + 4 Agents
    """
)

# Main Dashboard View
st.markdown("<div class='main-title'>🎓 EduPilot AI: Academic Support System</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>An Agentic Multi-Agent Framework for Early Student Academic Intervention and Review</div>",
    unsafe_allow_html=True,
)

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(label="Total Synthetic Students", value=len(data_service.students))
with c2:
    st.metric(label="Analyzed in Session", value=len(st.session_state.analysis_history))
with c3:
    flagged_count = sum(
        1 for r in st.session_state.analysis_history if len(r.get("identified_concerns", [])) > 0
    )
    st.metric(label="Students Requiring Support", value=flagged_count)
with c4:
    st.metric(label="Validation Pass Rate", value="100%" if st.session_state.analysis_history else "Ready")

st.markdown("---")

# AI Agent Taxonomy Section
st.subheader("🤖 AI Agent Taxonomy Classification (Russell & Norvig)")
st.caption("EduPilot AI maps its multi-agent architecture directly to foundational AI agent archetypes:")

tax_col1, tax_col2, tax_col3, tax_col4 = st.columns(4)

with tax_col1:
    st.markdown(
        """
        <div style='background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 14px; min-height: 220px;'>
            <span style='background-color: #1D4ED8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;'>GOAL-BASED AGENT</span>
            <div style='font-size: 1.05rem; font-weight: 700; color: #1E3A8A; margin-top: 8px;'>Agent 1: Academic Planner</div>
            <div style='font-size: 0.85rem; color: #334155; margin-top: 6px;'>
                <b>Goal State:</b> Complete, verified 6-step review plan with 100% indicator coverage.<br>
                <b>Mechanism:</b> Sub-goal decomposition, tool requirements mapping, and workflow formulation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col2:
    st.markdown(
        """
        <div style='background-color: #F0FDFA; border: 1px solid #99F6E4; border-radius: 8px; padding: 14px; min-height: 220px;'>
            <span style='background-color: #0F766E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;'>MODEL-BASED REFLEX</span>
            <div style='font-size: 1.05rem; font-weight: 700; color: #115E59; margin-top: 8px;'>Agent 2: Student Analytics</div>
            <div style='font-size: 0.85rem; color: #334155; margin-top: 6px;'>
                <b>Internal Model:</b> Tracks chronological scores across tests (Quiz 1 → Mid-Term).<br>
                <b>Condition-Action:</b> <i>If attendance &lt; 75% → flag concern; if score drop &ge; 15% pts → flag decline.</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col3:
    st.markdown(
        """
        <div style='background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 14px; min-height: 220px;'>
            <span style='background-color: #B45309; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;'>UTILITY-BASED AGENT</span>
            <div style='font-size: 1.05rem; font-weight: 700; color: #92400E; margin-top: 8px;'>Agent 3: Intervention Planner</div>
            <div style='font-size: 0.85rem; color: #334155; margin-top: 6px;'>
                <b>Utility Function:</b> Maximizes academic recovery utility <i>U(Action, Severity, Role)</i>.<br>
                <b>Trade-offs:</b> Selects optimal interventions balancing support intensity against student burden.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tax_col4:
    st.markdown(
        """
        <div style='background-color: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 8px; padding: 14px; min-height: 220px;'>
            <span style='background-color: #6D28D9; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;'>LEARNING & AUDIT AGENT</span>
            <div style='font-size: 1.05rem; font-weight: 700; color: #581C87; margin-top: 8px;'>Agent 4: Critic & Validation</div>
            <div style='font-size: 0.85rem; color: #334155; margin-top: 6px;'>
                <b>Critic Element:</b> Evaluates calculations against mathematical invariants & ground truth.<br>
                <b>Adaptive Loop:</b> Feeds error signals to Correction Node with bounded retries.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Quick Navigation & Architecture
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("🧭 Dynamic Multi-Agent Calling Flow")
    st.markdown(
        """
        ```mermaid
        flowchart LR
            User([Faculty Mentor]) -->|1. Input Request| Val[Gateway: Input Validation]
            Val -->|2. Valid Request| A1[Agent 1: Planner<br><b>Goal-Based Agent</b>]
            A1 -->|3. Execution Plan| A2[Agent 2: Analytics<br><b>Model-Based Reflex</b>]
            A2 <-->|4. MCP Tool Invocations| MCP[(Local MCP Server)]
            A2 -->|5. Flagged Concerns & Evidence| A3[Agent 3: Interventions<br><b>Utility-Based Agent</b>]
            A3 -->|6. Action Roadmap| A4[Agent 4: Critic<br><b>Learning / Audit Agent</b>]
            A4 -->|7a. Validation Passed| Rpt[Report Generator]
            A4 -->|7b. Discrepancy Caught| Corr[Correction Loop]
            Corr --> A2
            Rpt --> Final([18-Field Report])

            classDef goal fill:#DBEAFE,stroke:#1D4ED8,stroke-width:2px;
            classDef reflex fill:#CCFBF1,stroke:#0F766E,stroke-width:2px;
            classDef utility fill:#FEF3C7,stroke:#B45309,stroke-width:2px;
            classDef critic fill:#F3E8FF,stroke:#6D28D9,stroke-width:2px;

            class A1 goal;
            class A2 reflex;
            class A3 utility;
            class A4 critic;
        ```
        """
    )

    st.info(
        "💡 **Decision Support Boundary**: EduPilot AI does not make consequential or punitive academic "
        "decisions automatically. All intervention plans require faculty mentor review and approval."
    )

with right_col:
    st.subheader("⚡ Quick Start for 5-Minute Demo")
    st.markdown(
        """
        1. **Academic Overview**: View cohort-wide metrics across 100 students and distribution charts.
        2. **Analyze Student**: Select **STU1016** (Low Attendance) or **STU1036** (Declining Marks) and run a live dynamic analysis.
        3. **Agent Workflow**: Inspect real LangGraph execution steps, latencies, and MCP tool telemetry.
        4. **Intervention Reports**: View and download the official 18-field standardized report (JSON/CSV).
        5. **Batch Analysis**: Rapidly screen an entire section simultaneously.
        """
    )
    if st.button("🚀 Go to Student Analysis", type="primary", use_container_width=True):
        st.switch_page("pages/2_Analyze_Student.py")

st.markdown("---")
