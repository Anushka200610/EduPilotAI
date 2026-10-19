"""Page 1: Academic Overview for EduPilot AI.

Presents aggregate synthetic cohort metrics, attendance and assessment
distributions, concern category breakdown, and session audit history.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.data_service import data_service
from config.settings import settings

st.set_page_config(page_title="Academic Overview | EduPilot AI", page_icon="📈", layout="wide")

st.title("📈 Academic Overview & Cohort Analytics")
st.caption("Aggregated analytics across the 100-student synthetic dataset (Fall 2026)")

# Calculate Cohort Statistics directly from real data
df_att = data_service.attendance.copy()
df_asm = data_service.assessments.copy()
df_asg = data_service.assignments.copy()
df_stu = data_service.students.copy()

# Attendance % per student
att_grouped = df_att.groupby("student_id")[["classes_attended", "classes_held"]].sum()
att_grouped["attendance_pct"] = (att_grouped["classes_attended"] / att_grouped["classes_held"]) * 100.0
avg_cohort_att = round(att_grouped["attendance_pct"].mean(), 1)
low_att_count = (att_grouped["attendance_pct"] < settings.thresholds.min_attendance_pct).sum()

# Marks % per assessment
df_asm["score_pct"] = (df_asm["marks_obtained"] / df_asm["maximum_marks"]) * 100.0
avg_cohort_score = round(df_asm["score_pct"].mean(), 1)
low_marks_count = (df_asm["score_pct"] < settings.thresholds.min_passing_marks_pct).sum()

# Missing assignments count
missing_asg_count = (df_asg["submission_status"].isin(["MISSING", "PENDING"])).sum()

# Top KPI row
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Cohort Size", f"{len(df_stu)} Students")
with k2:
    st.metric("Avg Cohort Attendance", f"{avg_cohort_att}%")
with k3:
    st.metric("Avg Exam Score", f"{avg_cohort_score}%")
with k4:
    st.metric("Attendance Alerts (<75%)", f"{low_att_count} Students", delta="-Needs Review", delta_color="inverse")
with k5:
    session_count = len(st.session_state.get("analysis_history", []))
    st.metric("Session Analyzed", f"{session_count} Students")

st.markdown("---")

# Visual Charts Row 1
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Cohort Attendance Distribution")
    fig_att = px.histogram(
        att_grouped,
        x="attendance_pct",
        nbins=20,
        title="Distribution of Overall Student Attendance (%)",
        labels={"attendance_pct": "Attendance (%)"},
        color_discrete_sequence=["#2563EB"],
    )
    fig_att.add_vline(
        x=settings.thresholds.min_attendance_pct,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Threshold ({settings.thresholds.min_attendance_pct}%)",
    )
    fig_att.update_layout(bargap=0.08, height=360)
    st.plotly_chart(fig_att, use_container_width=True)

with col_right:
    st.subheader("📚 Subject-Wise Assessment Average (%)")
    subj_scores = df_asm.groupby("subject_id")["score_pct"].mean().reset_index()
    fig_subj = px.bar(
        subj_scores,
        x="subject_id",
        y="score_pct",
        color="subject_id",
        title="Average Assessment Marks by Subject",
        labels={"score_pct": "Average Marks (%)", "subject_id": "Subject Code"},
        text_auto=".1f",
    )
    fig_subj.add_hline(
        y=settings.thresholds.min_passing_marks_pct,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Passing Mark ({settings.thresholds.min_passing_marks_pct}%)",
    )
    fig_subj.update_layout(height=360, showlegend=False)
    st.plotly_chart(fig_subj, use_container_width=True)

# Visual Charts Row 2
col3, col4 = st.columns(2)

with col3:
    st.subheader("🎯 Assignment Submission Status")
    asg_counts = df_asg["submission_status"].value_counts().reset_index()
    asg_counts.columns = ["status", "count"]
    color_map = {"SUBMITTED": "#10B981", "LATE": "#F59E0B", "MISSING": "#EF4444", "PENDING": "#6B7280"}
    fig_asg = px.pie(
        asg_counts,
        names="status",
        values="count",
        title="Global Assignment Completion Breakdown",
        color="status",
        color_discrete_map=color_map,
        hole=0.45,
    )
    fig_asg.update_layout(height=340)
    st.plotly_chart(fig_asg, use_container_width=True)

with col4:
    st.subheader("🚨 Pre-Programmed Archetype Breakdown")
    meta = data_service.scenarios_meta
    archetypes = [v.get("archetype") for v in meta.values()]
    df_arch = pd.Series(archetypes).value_counts().reset_index()
    df_arch.columns = ["archetype", "count"]
    fig_arch = px.bar(
        df_arch,
        x="count",
        y="archetype",
        orientation="h",
        title="Synthetic Benchmark Scenario Groups (100 Students)",
        color="archetype",
        text="count",
    )
    fig_arch.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig_arch, use_container_width=True)

st.markdown("---")

# Recent Analysis History
st.subheader("🕒 Recent Analysis Sessions")
history = st.session_state.get("analysis_history", [])
if history:
    from tools.report_tools import export_reports_to_dataframe
    df_history = export_reports_to_dataframe(history)
    st.dataframe(
        df_history[
            [
                "report_id",
                "student_id",
                "overall_attendance_pct",
                "assessment_average_pct",
                "concerns_count",
                "final_status",
                "responsible_role",
            ]
        ],
        use_container_width=True,
    )
else:
    st.info("No students analyzed yet in this session. Head to **Analyze Student** to initiate analysis.")
