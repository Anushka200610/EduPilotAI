"""Page 2: Analyze Student for EduPilot AI.

Enables deep-dive single student academic investigation powered by the LangGraph
multi-agent workflow, MCP data tools, and adversarial Critic validation.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.data_service import data_service
from orchestration.graph import run_student_analysis
from config.settings import settings

st.set_page_config(page_title="Analyze Student | EduPilot AI", page_icon="🔍", layout="wide")

st.title("🔍 Student Academic Performance & Intervention Analysis")
st.caption("Investigate individual student records through the multi-agent LangGraph pipeline")

# Filter and Student Selection Controls
f_col1, f_col2, f_col3 = st.columns([1, 1, 2])

with f_col1:
    section_filter = st.selectbox("Filter Section", ["All", "A", "B", "C"], index=0)
with f_col2:
    program_filter = st.selectbox(
        "Filter Program", ["All", "B.Tech AIML", "B.Tech CSE", "B.Tech Data Science"], index=0
    )

df_students = data_service.students.copy()
if section_filter != "All":
    df_students = df_students[df_students["section"] == section_filter]
if program_filter != "All":
    df_students = df_students[df_students["program"] == program_filter]

# Build user-friendly dropdown options with scenario archetype tags
scenarios_meta = data_service.scenarios_meta
options = []
student_id_list = df_students["student_id"].tolist()

for sid in student_id_list:
    meta = scenarios_meta.get(sid, {})
    arch = meta.get("archetype", "UNKNOWN")
    options.append(f"{sid} — [{arch}]")

with f_col3:
    selected_option = st.selectbox(
        "Select Synthetic Student Record",
        options,
        index=0 if options else None,
        help="Choose a student to analyze. Archetypes demonstrate varied academic situations.",
    )

selected_student_id = selected_option.split(" — ")[0] if selected_option else None

# Analysis Objective
analysis_obj = st.text_input(
    "Analysis Objective",
    value="Comprehensive Mid-Term Academic Review & Early Intervention Screening",
    help="Custom objective incorporated into the execution plan and report.",
)

# Run Analysis Button
c_btn, c_note = st.columns([1, 3])
with c_btn:
    run_clicked = st.button("🚀 Run Agentic Analysis", type="primary", use_container_width=True)
with c_note:
    st.markdown(
        "<span style='color: #6B7280; font-size: 0.9rem;'>Orchestrates Planning, Analytics (MCP), "
        "Intervention, and Critic Agents with real-time verification.</span>",
        unsafe_allow_html=True,
    )

# Execution trigger
if run_clicked and selected_student_id:
    import time
    with st.status(f"⚡ Orchestrating Multi-Agent Pipeline for {selected_student_id}...", expanded=True) as status_box:
        st.write("🛡️ **Step 1: Input Validation Gateway** — Checking student identifier regex & synthetic database integrity...")
        time.sleep(0.15)
        st.write("📋 **Step 2: Agent 1 (Academic Planner)** `[Goal-Based Agent]` — Decomposing review request into 6 sub-goals...")
        time.sleep(0.15)
        st.write("📊 **Step 3: Agent 2 (Student Analytics)** `[Model-Based Reflex Agent]` — Calling MCP tools & evaluating threshold rules...")
        time.sleep(0.15)
        st.write("💡 **Step 4: Agent 3 (Intervention Planner)** `[Utility-Based Agent]` — Maximizing recovery utility U(Action, Severity, Role)...")
        time.sleep(0.15)
        st.write("🔍 **Step 5: Agent 4 (Critic & Validation)** `[Learning & Verification Agent]` — Adversarially recomputing invariants & bounds...")
        result_state = run_student_analysis(selected_student_id, analysis_objective=analysis_obj)
        time.sleep(0.15)
        st.write("📑 **Step 6: Report Generator Node** — Assembling standardized 18-field documentation...")
        status_box.update(
            label=f"✅ Multi-Agent Review Completed ({result_state['final_report']['final_status']})",
            state="complete",
            expanded=False,
        )

        st.session_state.latest_state = result_state

        # Check if already in history, if so update, else prepend
        st.session_state.analysis_history = [
            r for r in st.session_state.analysis_history if r.get("student_id") != selected_student_id
        ]
        st.session_state.analysis_history.insert(0, result_state["final_report"])

# Display Analysis if latest_state exists
state = st.session_state.get("latest_state")

if state and state.get("student_id") == selected_student_id:
    st.markdown("---")
    report = state.get("final_report", {})
    profile = state.get("profile", {})
    indicators = state.get("indicators", {})
    concerns = state.get("concerns", [])
    interventions = state.get("interventions", [])
    validation = state.get("validation_results", {})
    final_status = report.get("final_status", "UNKNOWN")

    # Dynamic Agent Flow Calling Sequence Bar
    st.subheader("⚡ Agent Calling Sequence for this Investigation")
    st.markdown(
        """
        <div style='background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 1rem;'>
            <div style='display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between;'>
                <div style='background-color: #E2E8F0; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    1. Gateway<br><span style='color: #475569; font-size: 0.75rem;'>Deterministic</span>
                </div>
                <div style='color: #94A3B8; font-weight: bold;'>➔</div>
                <div style='background-color: #DBEAFE; border: 1px solid #93C5FD; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    2. Planner Agent<br><span style='color: #1D4ED8; font-size: 0.75rem;'>Goal-Based</span>
                </div>
                <div style='color: #94A3B8; font-weight: bold;'>➔</div>
                <div style='background-color: #CCFBF1; border: 1px solid #5EEAD4; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    3. Analytics Agent<br><span style='color: #0F766E; font-size: 0.75rem;'>Model-Based Reflex (MCP)</span>
                </div>
                <div style='color: #94A3B8; font-weight: bold;'>➔</div>
                <div style='background-color: #FEF3C7; border: 1px solid #FCD34D; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    4. Intervention Agent<br><span style='color: #B45309; font-size: 0.75rem;'>Utility-Based</span>
                </div>
                <div style='color: #94A3B8; font-weight: bold;'>➔</div>
                <div style='background-color: #F3E8FF; border: 1px solid #D8B4FE; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    5. Critic & Validator<br><span style='color: #6D28D9; font-size: 0.75rem;'>Learning / Audit Agent</span>
                </div>
                <div style='color: #94A3B8; font-weight: bold;'>➔</div>
                <div style='background-color: #DCFCE7; border: 1px solid #86EFAC; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;'>
                    6. Report Generator<br><span style='color: #15803D; font-size: 0.75rem;'>18-Field Output</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Header with Profile & Status
    h1, h2 = st.columns([3, 1])
    with h1:
        st.subheader(f"Academic Profile: {selected_student_id}")
        st.markdown(
            f"**Program**: {profile.get('program', 'N/A')} | "
            f"**Semester**: {profile.get('semester', 'N/A')} | "
            f"**Section**: {profile.get('section', 'N/A')} | "
            f"**Term**: {report.get('academic_term', 'Fall 2026')}"
        )
        if profile.get("archetype_description"):
            st.info(f"📌 **Scenario Profile**: {profile.get('archetype_description')}")

    with h2:
        status_color = "#10B981" if final_status == "VALIDATED" else "#EF4444"
        st.markdown(
            f"""
            <div style='background-color: #F3F4F6; padding: 12px; border-radius: 8px; text-align: center;'>
                <div style='font-size: 0.8rem; color: #4B5563;'>AUDIT STATUS</div>
                <div style='font-size: 1.2rem; font-weight: 700; color: {status_color};'>{final_status}</div>
                <div style='font-size: 0.75rem; color: #6B7280;'>ID: {report.get('report_id', '')[:18]}...</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Key Indicator Metrics Cards
    att_info = indicators.get("attendance", {})
    asm_info = indicators.get("assessments", {})
    asg_info = indicators.get("assignments", {})

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        att_pct = att_info.get("overall_pct", 0.0)
        att_delta = f"{round(att_pct - settings.thresholds.min_attendance_pct, 1)}% vs threshold"
        st.metric(
            "Overall Attendance",
            f"{att_pct:.1f}%",
            delta=att_delta,
            delta_color="normal" if att_pct >= settings.thresholds.min_attendance_pct else "inverse",
        )
    with m2:
        asm_avg = asm_info.get("overall_average_pct", 0.0)
        asm_delta = f"{round(asm_avg - settings.thresholds.min_passing_marks_pct, 1)}% vs passing"
        st.metric(
            "Assessment Average",
            f"{asm_avg:.1f}%",
            delta=asm_delta,
            delta_color="normal" if asm_avg >= settings.thresholds.min_passing_marks_pct else "inverse",
        )
    with m3:
        comp_pct = asg_info.get("completion_pct", 0.0)
        st.metric("Assignment Completion", f"{comp_pct:.1f}%", delta=f"{asg_info.get('missing', 0)} Missing")
    with m4:
        priority = state.get("support_priority", "NONE")
        priority_colors = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#3B82F6", "NONE": "#10B981"}
        st.markdown(
            f"""
            <div style='background-color: #F9FAFB; padding: 10px; border-radius: 8px; border: 1px solid #E5E7EB;'>
                <div style='font-size: 0.8rem; color: #6B7280;'>SUPPORT PRIORITY</div>
                <div style='font-size: 1.5rem; font-weight: 700; color: {priority_colors.get(priority, "#10B981")};'>
                    {priority}
                </div>
                <div style='font-size: 0.75rem; color: #4B5563;'>{len(concerns)} concern(s) flagged</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Agent 1 Plan Viewer
    with st.expander("📋 View Academic Planning Agent's Formulated Plan [Goal-Based Agent]"):
        plan = state.get("execution_plan", {})
        st.markdown(f"**Agent**: `Academic Planning Agent` | **Taxonomy Class**: `Goal-Based Agent`")
        st.markdown(f"**Goal**: Decompose review objective into 6 structured sub-goals to reach complete academic evaluation state.")
        st.markdown(f"**Objective**: *{plan.get('objective', 'Comprehensive Review')}*")
        st.markdown(f"**Indicators Specified**: {', '.join(plan.get('indicators_to_compute', []))}")
        steps = plan.get("steps", [])
        if steps:
            df_plan = pd.DataFrame([
                {
                    "Step": s.get("step_index"),
                    "Sub-Goal / Task": s.get("name"),
                    "Agent Responsible": s.get("agent"),
                    "Agent Type": s.get("agent_type", "Goal-Based Agent"),
                    "Status": s.get("status"),
                }
                for s in steps
            ])
            st.dataframe(df_plan, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Detailed Charts: Attendance by Subject & Assessment Trajectory (Agent 2)
    st.markdown(
        """
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <h3 style='margin: 0;'>📊 Subject-Wise Analytics & Trajectory</h3>
            <span style='background-color: #0F766E; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: bold;'>
                AGENT 2: MODEL-BASED REFLEX AGENT (MCP Tools)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("**Subject-Wise Attendance (%)**")
        subj_att = att_info.get("subjects", {})
        if subj_att:
            df_subj_att = pd.DataFrame([
                {"subject": k, "percentage": v.get("percentage", 0.0), "held": v.get("classes_held", 0), "attended": v.get("classes_attended", 0)}
                for k, v in subj_att.items()
            ])
            fig_subj_att = px.bar(
                df_subj_att,
                x="subject",
                y="percentage",
                color="percentage",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                text_auto=".1f",
                range_y=[0, 105],
                title=f"Attendance by Subject for {selected_student_id}",
            )
            fig_subj_att.add_hline(
                y=settings.thresholds.min_attendance_pct,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Min Required ({settings.thresholds.min_attendance_pct}%)",
            )
            fig_subj_att.update_layout(height=340, showlegend=False)
            st.plotly_chart(fig_subj_att, use_container_width=True)
        else:
            st.warning("No attendance records found.")

    with c_right:
        st.markdown("**Assessment Trajectory (Quiz 1 vs Mid-Term)**")
        subj_asm = asm_info.get("subjects", {})
        if subj_asm:
            plot_rows = []
            for subj, data in subj_asm.items():
                for test in data.get("assessments", []):
                    plot_rows.append({
                        "subject": subj,
                        "assessment": test["name"],
                        "score_pct": test["pct"],
                    })
            if plot_rows:
                df_plot = pd.DataFrame(plot_rows)
                fig_trend = px.line(
                    df_plot,
                    x="assessment",
                    y="score_pct",
                    color="subject",
                    markers=True,
                    title="Score Trajectory Across Sequential Tests",
                    range_y=[0, 105],
                )
                fig_trend.add_hline(
                    y=settings.thresholds.min_passing_marks_pct,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Passing ({settings.thresholds.min_passing_marks_pct}%)",
                )
                fig_trend.update_layout(height=340)
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No assessment records found.")

    st.markdown("---")

    # Identified Concerns with Verifiable Evidence
    st.subheader(f"🚨 Identified Academic Concerns ({len(concerns)})")
    if concerns:
        for idx, c in enumerate(concerns):
            sev = c.get("severity", "MEDIUM")
            sev_color = "#EF4444" if sev in ["CRITICAL", "HIGH"] else "#F59E0B"
            with st.container():
                st.markdown(
                    f"""
                    <div style='background-color: #FEF2F2 if "{sev}"=="HIGH" else #FFFBEB; border-left: 4px solid {sev_color}; padding: 12px; margin-bottom: 8px; border-radius: 4px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b>{c.get('rule_name')}</b>
                            <span style='background-color: {sev_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;'>{sev}</span>
                        </div>
                        <div style='margin-top: 4px; color: #1F2937;'>{c.get('description')}</div>
                        <div style='margin-top: 6px; font-size: 0.85rem; color: #4B5563;'>
                            <b>Verifiable Evidence:</b> <code>{c.get('evidence')}</code>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.success("✅ No academic concerns identified. Student is progressing satisfactorily across all metrics.")

    st.markdown("---")

    # Recommended Academic Interventions (Agent 3)
    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <h3 style='margin: 0;'>📋 Formulated Intervention Action Plan ({len(interventions)})</h3>
            <span style='background-color: #B45309; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: bold;'>
                AGENT 3: UTILITY-BASED AGENT (Payoff Optimization)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for idx, item in enumerate(interventions):
        with st.expander(f"Action #{idx + 1}: {item.get('concern')}", expanded=True):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**Recommended Action**: {item.get('recommended_action')}")
                st.markdown(f"**Supporting Evidence**: `{item.get('supporting_evidence')}`")
            with col_b:
                st.markdown(f"**Responsible Role**: `{item.get('responsible_role')}`")
                st.markdown(f"**Review Timeline**: `{item.get('suggested_review_period')}`")
                st.markdown(f"**Target Outcome**: `{item.get('measurable_outcome')}`")

    st.markdown("---")

    # Critic & Validation Audit Box (Agent 4)
    st.markdown(
        """
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <h3 style='margin: 0;'>🛡️ Critic & Validation Agent Audit Trail</h3>
            <span style='background-color: #6D28D9; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: bold;'>
                AGENT 4: LEARNING & VERIFICATION AGENT (Adversarial Critic)
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    v_c1, v_c2 = st.columns([1, 2])
    with v_c1:
        is_valid = validation.get("valid", False)
        st.metric("Critic Checks Passed", f"{validation.get('passed_checks', 0)}/{validation.get('total_checks', 0)}")
        if is_valid:
            st.success("✅ Critic Invariant Checks Passed")
        else:
            st.error("❌ Critic Discrepancies Caught")
    with v_c2:
        st.markdown("**Checks Executed**:")
        for chk in validation.get("checks_performed", []):
            mark = "✅" if chk.get("passed", False) else "❌"
            st.markdown(f"- {mark} **{chk.get('check')}**")

    # Expandable Mathematical Trace
    with st.expander("📐 Step-by-Step Calculation Details & Formulas"):
        st.markdown(
            """
            **Attendance Percentage Formula**:
            $$\\text{Attendance (\\%)} = \\frac{\\text{Classes Attended}}{\\text{Classes Held}} \\times 100$$

            **Assessment Percentage Formula**:
            $$\\text{Score (\\%)} = \\frac{\\text{Marks Obtained}}{\\text{Maximum Marks}} \\times 100$$

            **Performance Decline Formula**:
            $$\\Delta = \\text{Score}(\\text{Quiz 1}) - \\text{Score}(\\text{Mid-Term})$$
            Triggered if $\\Delta \\ge 15\\%\\text{ pts}$.
            """
        )
else:
    st.info("👆 Select a student above and click **Run Agentic Analysis** to view the results.")
