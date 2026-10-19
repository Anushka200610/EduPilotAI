"""Page 5: Batch Analysis for EduPilot AI.

Enables faculty to screen entire class sections or student cohorts simultaneously,
identifying students needing priority support and exporting batch summaries.
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

from services.data_service import data_service
from orchestration.graph import run_student_analysis
from tools.report_tools import export_reports_to_dataframe

st.set_page_config(page_title="Batch Analysis | EduPilot AI", page_icon="👥", layout="wide")

st.title("👥 Batch Student Cohort Analysis")
st.caption("Screen multiple student records simultaneously to prioritize faculty interventions")

# Filter / Selection Options
b_col1, b_col2 = st.columns([1, 2])
with b_col1:
    batch_mode = st.radio("Cohort Scope", ["Section-Wise", "Scenario Archetype", "Full Cohort (100)"], index=0)

df_all = data_service.students.copy()
selected_students = []

with b_col2:
    if batch_mode == "Section-Wise":
        sec = st.selectbox("Select Section", ["Section A", "Section B", "Section C"], index=0)
        sec_letter = sec.split(" ")[1]
        selected_students = df_all[df_all["section"] == sec_letter]["student_id"].tolist()
        st.write(f"Selected **{len(selected_students)} students** enrolled in Section {sec_letter}.")
    elif batch_mode == "Scenario Archetype":
        meta = data_service.scenarios_meta
        arch_options = sorted(list({v.get("archetype") for v in meta.values()}))
        chosen_arch = st.selectbox("Select Archetype", arch_options)
        selected_students = [sid for sid, v in meta.items() if v.get("archetype") == chosen_arch]
        st.write(f"Selected **{len(selected_students)} students** with archetype: `{chosen_arch}`.")
    else:
        selected_students = df_all["student_id"].tolist()
        st.write(f"Selected all **{len(selected_students)} students** across all sections.")

# Run Batch Analysis Button
if st.button(f"⚡ Execute Batch Screening for {len(selected_students)} Students", type="primary"):
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    batch_states = []
    total = len(selected_students)

    for idx, sid in enumerate(selected_students):
        status_text.text(f"Analyzing {sid} ({idx + 1}/{total})...")
        state = run_student_analysis(sid)
        batch_states.append(state)
        # Add to global session history
        st.session_state.analysis_history = [
            r for r in st.session_state.analysis_history if r.get("student_id") != sid
        ]
        st.session_state.analysis_history.insert(0, state["final_report"])
        progress_bar.progress((idx + 1) / total)

    status_text.text("Batch screening completed successfully!")
    st.session_state.batch_results = batch_states
    st.success(f"Successfully processed {len(batch_states)} student records.")

# Display Batch Results
batch_res = st.session_state.get("batch_results", [])

if batch_res:
    st.markdown("---")
    st.subheader("📊 Batch Screening Results & Support Prioritization")

    # Metrics
    total_screened = len(batch_res)
    requiring_support = sum(1 for s in batch_res if len(s.get("concerns", [])) > 0)
    high_priority = sum(1 for s in batch_res if s.get("support_priority") == "HIGH")
    medium_priority = sum(1 for s in batch_res if s.get("support_priority") == "MEDIUM")
    no_concerns = total_screened - requiring_support

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Screened", total_screened)
    with k2:
        st.metric("Requiring Support", requiring_support, delta=f"{round(requiring_support/total_screened*100, 1)}%")
    with k3:
        st.metric("High Priority Action", high_priority, delta="Urgent Review", delta_color="inverse")
    with k4:
        st.metric("Satisfactory Progress", no_concerns)

    st.markdown("---")

    # Priority Table
    reports_list = [s["final_report"] for s in batch_res]
    df_batch = export_reports_to_dataframe(reports_list)

    # Export Button
    csv_bytes = df_batch.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Export Batch Summary (CSV)",
        data=csv_bytes,
        file_name="edupilot_batch_summary.csv",
        mime="text/csv",
    )

    # Highlight High Priority
    st.dataframe(
        df_batch[
            [
                "student_id",
                "overall_attendance_pct",
                "assessment_average_pct",
                "assignment_completion_pct",
                "concerns_count",
                "concerns_summary",
                "validation_passed",
                "final_status",
            ]
        ].sort_values(by="concerns_count", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
