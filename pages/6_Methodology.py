"""Page 6: Methodology, Limitations, and Ethics for EduPilot AI.

Comprehensive academic documentation covering the problem domain,
agent architecture, LangGraph orchestration, MCP tools, deterministic rules,
empirical evaluation benchmarks, ethical safeguards, and limitations.
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
from config.settings import DOCS_DIR
from services.evaluation_service import evaluation_service

st.set_page_config(page_title="Methodology | EduPilot AI", page_icon="📖", layout="wide")

st.title("📖 System Methodology, Architecture & Ethics")
st.caption("Detailed academic specifications for AIML Second-Year Undergraduate CA-3 Assignment")

tabs = st.tabs([
    "1. Problem & Architecture",
    "2. Agent Roles & LangGraph",
    "3. MCP & Decision Rules",
    "4. Empirical Evaluation",
    "5. Ethics, Limitations & Future Scope",
])

# -----------------------------------------------------------------------------
# TAB 1: Problem & Architecture
# -----------------------------------------------------------------------------
with tabs[0]:
    st.subheader("1. Problem Statement & Domain Context")
    st.markdown(
        """
        Higher education institutions maintain disparate records for attendance, assessment marks,
        and coursework submissions across various departments and Learning Management Systems (LMS).
        Faculty mentors must examine these records manually to identify students who may need academic support.

        **Key Inefficiencies in Existing Workflows**:
        - **Delayed Intervention**: Academic review often occurs only after mid-term exams, when remediation time is scarce.
        - **Cognitive Overload**: Cross-referencing attendance spreadsheets and test score sheets across 4-6 subjects is labor-intensive.
        - **Inconsistent Support**: Interventions often lack structured timelines, assigned faculty roles, or measurable milestones.

        **EduPilot AI Solution**:
        An Agentic AI Proof of Concept (PoC) that orchestrates four specialized agents to automate data aggregation,
        detect emerging academic risks using transparent rules, generate evidence-backed intervention roadmaps,
        and independently audit calculations before presenting findings to human faculty mentors.
        """
    )

    st.markdown("---")
    st.subheader("2. End-to-End System Architecture")
    st.markdown(
        """
        ```mermaid
        flowchart TD
            subgraph UserLayer[Faculty User Interface]
                UI[Streamlit Multi-Page Web App]
            end

            subgraph OrchestrationLayer[LangGraph Multi-Agent Orchestrator]
                IV[Input Validation Node]
                Planner[Agent 1: Academic Planning Agent]
                Analytics[Agent 2: Student Analytics Agent]
                Intervention[Agent 3: Intervention Planning Agent]
                Critic[Agent 4: Critic & Validation Agent]
                Correction[Correction & Recalculation Node]
                ReportGen[Report Generator Node]
            end

            subgraph ToolLayer[MCP Standard Tool Layer]
                MCPServer[Local Academic MCP Server]
                MCPTools[7 Academic Tools]
            end

            subgraph DataLayer[Synthetic Data Store]
                CSV1[(students.csv)]
                CSV2[(attendance.csv)]
                CSV3[(assessments.csv)]
                CSV4[(assignments.csv)]
            end

            UI -->|Student Request| IV
            IV -->|Valid| Planner
            IV -->|Invalid| ReportGen
            Planner --> Analytics
            Analytics <-->|MCP Protocol stdio/json| MCPServer
            MCPServer --> MCPTools
            MCPTools <--> CSV1 & CSV2 & CSV3 & CSV4
            Analytics --> Intervention
            Intervention --> Critic
            Critic -->|Validation Passed| ReportGen
            Critic -->|Discrepancy Caught| Correction
            Correction --> Analytics
            ReportGen --> UI
        ```
        """
    )

# -----------------------------------------------------------------------------
# TAB 2: Agent Taxonomy & PEAS Model
# -----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("2. AI Agent Taxonomy & Theoretical Grounding (Russell & Norvig)")
    st.markdown(
        """
        In foundational Artificial Intelligence theory (*Russell & Norvig, "Artificial Intelligence: A Modern Approach", 4th Edition, Chapter 2*), 
        intelligent agents are classified into distinct architectural paradigms based on how they process percepts and select actions.
        EduPilot AI deliberately maps each of its four specialized agents to an explicit, textbook AI agent category:
        """
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            """
            ### 🎯 Agent 1: Goal-Based Agent
            - **System Role**: Academic Planning Agent
            - **Formal Definition**: A goal-based agent combines goal descriptions with information regarding the results of possible actions in order to choose actions that achieve the goal.
            - **Goal Formulation**: Given analysis objective $G = \\text{Objective}(\\text{Student ID})$, the agent formulates an ordered sequence of sub-goals $A = [a_1, a_2, \\dots, a_6]$ and specifies the required academic indicator dependencies.
            - **Informed Planning**: Downstream graph nodes do not execute arbitrarily; they are activated dynamically based on the plan constructed by this agent.
            """
        )

        st.markdown(
            """
            ### ⚖️ Agent 3: Utility-Based Agent
            - **System Role**: Intervention Planning Agent
            - **Formal Definition**: When multiple courses of action can achieve a goal, a utility function maps states to real numbers, quantifying the degree of desirability and resolving trade-offs.
            - **Utility Optimization**: Maximizes the pedagogical recovery utility function:
              $$U(A, S, R) = w_1 \\cdot \\text{Impact}(A, S) - w_2 \\cdot \\text{Burden}(A) + w_3 \\cdot \\text{Feasibility}(R)$$
              where $A$ is the recommended action, $S$ is concern severity, and $R$ is the assigned academic role (e.g., Course Instructor, Faculty Mentor, Head of Department).
            - **Prioritization**: Ranks high-severity composite risks (e.g. attendance failure + test failure) as HIGH priority, ensuring focused faculty attention without overburdening the student.
            """
        )

    with t2:
        st.markdown(
            """
            ### 🔍 Agent 2: Model-Based Reflex Agent
            - **System Role**: Student Analytics Agent
            - **Formal Definition**: A reflex agent that maintains an internal model of the world to track aspects of the environment that cannot be viewed in a single percept.
            - **Internal Model**: Tracks longitudinal progression over time (e.g., Quiz 1 $\\to$ Mid-Term Exam) and aggregates composite metrics across multiple academic terms.
            - **Condition-Action Reflex Rules**:
              - $\\text{Rule}_1$: $\\text{IF } \\text{Attendance} < 75\\% \\implies \\text{ATTENDANCE\\_LOW}$
              - $\\text{Rule}_2$: $\\text{IF } \\text{Score} < 40\\% \\implies \\text{ACADEMIC\\_PERFORMANCE\\_LOW}$
              - $\\text{Rule}_3$: $\\text{IF } \\Delta(\\text{Quiz 1}, \\text{Mid-Term}) \\ge 15\\%\\text{ pts} \\implies \\text{PERFORMANCE\\_DECLINE}$
              - $\\text{Rule}_4$: $\\text{IF } \\text{Missing Assignments} > 0 \\implies \\text{ASSIGNMENT\\_INCOMPLETE}$
            """
        )

        st.markdown(
            """
            ### 🛡️ Agent 4: Learning & Verification Agent
            - **System Role**: Critic & Validation Agent + Correction Node
            - **Formal Definition**: Features a distinct **Critic** element that evaluates the agent's actions against an external performance standard, feeding error signals to a **Learning Element** to modify future behavior.
            - **Mathematical Invariant Assertions**:
              - Invariant 1: $\\text{Attended Classes} \\le \\text{Classes Held}$
              - Invariant 2: $0 \\le \\text{Marks Obtained} \\le \\text{Maximum Marks}$
              - Invariant 3: $\\forall c \\in \\text{Concerns}, \\exists e \\in \\text{Evidence}$ (Grounded Evidence)
            - **Feedback Loop**: When invariants or thresholds fail, Critic routes back through the Correction Node for bounded retries (max 2), dynamically refining state before report synthesis.
            """
        )

    st.markdown("---")
    st.subheader("Formal PEAS Framework Comparison")
    st.markdown("Comprehensive specification across Performance Measure, Environment, Actuators, and Sensors:")

    peas_data = [
        {
            "Agent": "1. Academic Planner",
            "Agent Type": "Goal-Based Agent",
            "Performance Measure (P)": "Plan completeness, logical indicator ordering, schema validity",
            "Environment (E)": "Academic request, student registry, target term",
            "Actuators (A)": "Typed 6-step execution plan written to shared state",
            "Sensors (S)": "Student ID format string, requested analysis objective",
        },
        {
            "Agent": "2. Student Analytics",
            "Agent Type": "Model-Based Reflex Agent",
            "Performance Measure (P)": "Calculation accuracy, 100% evidence traceability, zero hallucinated data",
            "Environment (E)": "Synthetic academic records via local MCP tools",
            "Actuators (A)": "Subject indicators, flagged concerns list, traceable evidence records",
            "Sensors (S)": "MCP tool returns (JSON payloads from attendance, assessment, assignment tools)",
        },
        {
            "Agent": "3. Intervention Planner",
            "Agent Type": "Utility-Based Agent",
            "Performance Measure (P)": "Expected recovery utility, pedagogical feasibility, faculty role clarity",
            "Environment (E)": "Flagged concerns, evidence records, faculty role hierarchy",
            "Actuators (A)": "Prioritized interventions with roles, review periods (1-4 wks), measurable outcomes",
            "Sensors (S)": "Identified concerns list and quantitative evidence from Analytics Agent",
        },
        {
            "Agent": "4. Critic & Auditor",
            "Agent Type": "Learning & Verification Agent",
            "Performance Measure (P)": "Detection of invariant violations, discrepancy audit accuracy, verification soundness",
            "Environment (E)": "Emitted indicators, evidence claims, intervention plans, ground truth datasets",
            "Actuators (A)": "Audit status flag, discrepancy error list, conditional routing signal",
            "Sensors (S)": "Independent recomputations, raw data re-queries, invariant assertions",
        },
    ]
    st.dataframe(pd.DataFrame(peas_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("LangGraph State Machine & Conditional Edges")
    st.markdown(
        """
        - **Typed Shared State (`EduPilotState`)**: Backed by Python TypedDict containing plan, indicators, concerns, evidence, interventions, validation results, trace, and final report.
        - **Conditional Edge 1 (`after_input_validation`)**: Validates student ID format and existence. If invalid, bypasses downstream agents directly to report generation with `VALIDATION_FAILED`.
        - **Conditional Edge 2 (`after_critic`)**: Inspects Critic validation results. If checks pass, routes to report generator. If discrepancies are found and `retry_count < max_retries`, routes to correction node.
        - **Bounded Retries**: Enforces a strict limit (default 2 retries) to prevent infinite loops.
        """
    )

# -----------------------------------------------------------------------------
# TAB 3: MCP & Decision Rules
# -----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Model Context Protocol (MCP) Standard Integration")
    st.markdown(
        """
        EduPilot AI utilizes the official Python MCP SDK (`mcp` library). The local server exposes seven standardized tools:

        1. `get_student_profile(student_id)`: Retrieves demographic and enrollment details.
        2. `get_attendance_history(student_id)`: Fetches subject-wise class attendance counts.
        3. `get_assessment_results(student_id)`: Fetches chronological exam and quiz marks.
        4. `get_assignment_status(student_id)`: Fetches coursework submission states.
        5. `calculate_attendance(student_id)`: Computes percentage and flags attendance concerns.
        6. `calculate_academic_indicators(student_id)`: Aggregates composite indicators and concerns.
        7. `validate_intervention_plan(student_id, intervention_plan, indicators)`: Validates evidence grounding.

        **Communication Protocol**: Agents execute real tool calls through `mcp_client`, which serializes JSON arguments, executes through the MCP server interface, and records execution latency, status, and summaries for complete audit observability.
        """
    )

    st.markdown("---")
    st.subheader("Configurable Deterministic Decision Rules")
    st.markdown(
        """
        All decisions are transparent, deterministic, and rule-based:

        - **Attendance Concern (`ATTENDANCE_LOW`)**:
          $$\\text{Attendance} = \\frac{\\text{Attended Classes}}{\\text{Held Classes}} \\times 100 < 75.0\\%$$
        - **Assessment Concern (`ACADEMIC_PERFORMANCE_LOW`)**:
          $$\\text{Score} = \\frac{\\text{Marks Obtained}}{\\text{Maximum Marks}} \\times 100 < 40.0\\%$$
        - **Performance Decline (`PERFORMANCE_DECLINE`)**:
          $$\\Delta = \\text{Score}(\\text{Quiz 1}) - \\text{Score}(\\text{Mid-Term Exam}) \\ge 15.0\\%\\text{ pts}$$
        - **Assignment Incomplete (`ASSIGNMENT_INCOMPLETE`)**:
          $$\\text{Missing Assignments} > 0$$
        """
    )

# -----------------------------------------------------------------------------
# TAB 4: Empirical Evaluation
# -----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Reproducible Benchmark Evaluation Results")

    # Load from results file if available
    eval_file = DOCS_DIR / "evaluation_results.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)
    else:
        eval_data = evaluation_service.run_all_benchmarks()

    e1, e2, e3 = st.columns(3)
    with e1:
        st.metric("Scenarios Evaluated", eval_data.get("total_scenarios_evaluated", 10))
    with e2:
        st.metric("Rule Compliance Rate", f"{eval_data.get('rule_compliance_rate_pct', 100.0)}%")
    with e3:
        st.metric("Avg Execution Latency", f"{eval_data.get('average_latency_ms', 7.0)} ms")

    st.markdown("### Scenario Test Matrix")
    df_scen = pd.DataFrame(eval_data.get("scenarios", []))
    if not df_scen.empty:
        st.dataframe(
            df_scen[["scenario_id", "name", "student_id", "status", "latency_ms", "passed", "details"]],
            use_container_width=True,
            hide_index=True,
        )

    st.caption("Benchmark verified on deterministic synthetic test suites. Saved to docs/evaluation_results.json.")

# -----------------------------------------------------------------------------
# TAB 5: Ethics, Limitations & Future Scope
# -----------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Ethical Safeguards & Decision-Support Boundaries")
    st.markdown(
        """
        - **Human-in-the-Loop Decision Support**: EduPilot AI does not determine grades, academic penalties, suspension, or eligibility. It assists faculty mentors by surfacing verifiable evidence.
        - **No Hallucinated Intent**: The system never guesses why a student is struggling (e.g. personal issues, motivation). It strictly reports recorded numbers.
        - **Privacy Protection**: Synthetic IDs (e.g., STU1001) are used exclusively. No Personally Identifiable Information (PII) is processed.
        - **Auditable & Explainable**: Every concern is linked to a transparent mathematical calculation and rule name.
        """
    )

    st.markdown("---")
    st.subheader("System Limitations")
    st.markdown(
        """
        1. **Synthetic Data Boundaries**: Metrics and evaluation reflect synthetic distributions; real-world classrooms exhibit nuanced, unpredictable patterns.
        2. **Absence of Qualitative Context**: Medical leaves, sanctioned extracurriculars, or technical LMS submission glitches are not captured in static CSV records.
        3. **Deterministic Bias**: Fixed thresholds (e.g. 75%) may flag borderline students (74.8%) who do not genuinely require intensive faculty intervention.
        """
    )

    st.markdown("---")
    st.subheader("Future Scope & Extensions")
    st.markdown(
        """
        - Integration with institutional LMS (Canvas / Moodle) via authenticated REST/GraphQL MCP connectors.
        - Longitudinal multi-semester trend tracking.
        - Automated faculty reminder notifications and progress milestone tracking.
        """
    )
