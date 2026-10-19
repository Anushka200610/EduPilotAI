"""Page 4: Intervention Reports for EduPilot AI.

Presents the 18-field standardized Academic Intervention Reports,
session audit history, and one-click JSON/CSV export capabilities.
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
from tools.report_tools import export_reports_to_dataframe

st.set_page_config(page_title="Intervention Reports | EduPilot AI", page_icon="📋", layout="wide")

st.title("📋 Academic Intervention Reports")
st.caption("Standardized 18-field decision-support documentation for faculty and departmental records")

history = st.session_state.get("analysis_history", [])

if not history:
    st.info("No reports generated yet in this session. Analyze students in **Analyze Student** or **Batch Analysis** first.")
    if st.button("Go to Analyze Student"):
        st.switch_page("pages/2_Analyze_Student.py")
else:
    # Summary Table with Export
    df_export = export_reports_to_dataframe(history)

    exp_col1, exp_col2 = st.columns([3, 1])
    with exp_col1:
        st.subheader(f"📑 Session Reports Archive ({len(history)} Reports)")
    with exp_col2:
        csv_data = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Session CSV",
            data=csv_data,
            file_name="edupilot_session_reports.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(
        df_export[
            [
                "report_id",
                "student_id",
                "overall_attendance_pct",
                "assessment_average_pct",
                "assignment_completion_pct",
                "concerns_count",
                "validation_passed",
                "final_status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Detailed Single Report Viewer
    st.subheader("🔍 Inspect Full 18-Field Report")
    report_options = [f"{r.get('report_id')} ({r.get('student_id')})" for r in history]
    selected_rep_str = st.selectbox("Select Report to Inspect", report_options)

    selected_report_id = selected_rep_str.split(" (")[0]
    selected_report = next((r for r in history if r.get("report_id") == selected_report_id), history[0])

    # Download Individual Report as JSON
    json_bytes = json.dumps(selected_report, indent=2).encode("utf-8")
    st.download_button(
        label=f"💾 Download {selected_report.get('report_id')}.json",
        data=json_bytes,
        file_name=f"{selected_report.get('report_id')}.json",
        mime="application/json",
    )

    # Visual Inspection of the 18 Standard Fields
    st.markdown("### Standardized 18-Field Documentation")

    r_c1, r_c2, r_c3 = st.columns(3)
    with r_c1:
        st.markdown(f"**1. Report ID**: `{selected_report.get('report_id')}`")
        st.markdown(f"**2. Timestamp**: `{selected_report.get('timestamp')}`")
        st.markdown(f"**3. Student ID**: `{selected_report.get('student_id')}`")
        st.markdown(f"**4. Academic Term**: `{selected_report.get('academic_term')}`")
        st.markdown(f"**5. Objective**: {selected_report.get('analysis_objective')}")
        st.markdown(f"**6. Plan Steps**: {len(selected_report.get('execution_plan', []))} Steps")
    with r_c2:
        att = selected_report.get("attendance_indicators", {})
        asm = selected_report.get("assessment_indicators", {})
        asg = selected_report.get("assignment_indicators", {})
        st.markdown(f"**7. Attendance Indicator**: Overall `{att.get('overall_pct', 0.0)}%`")
        st.markdown(f"**8. Assessment Indicator**: Average `{asm.get('overall_average_pct', 0.0)}%`")
        st.markdown(f"**9. Assignment Indicator**: Rate `{asg.get('completion_pct', 0.0)}%`")
        st.markdown(f"**10. Identified Concerns**: {len(selected_report.get('identified_concerns', []))} Flagged")
        st.markdown(f"**11. Supporting Evidence**: {len(selected_report.get('supporting_evidence', []))} Traceable Items")
        st.markdown(f"**12. Recommended Interventions**: {len(selected_report.get('recommended_interventions', []))} Proposed")
    with r_c3:
        st.markdown(f"**13. Responsible Role**: `{selected_report.get('responsible_academic_role')}`")
        st.markdown(f"**14. Review Period**: `{selected_report.get('suggested_review_period')}`")
        st.markdown(f"**15. Expected Outcomes**: {len(selected_report.get('expected_measurable_outcome', []))} Defined")
        st.markdown(f"**16. Data Notes & Limitations**: {len(selected_report.get('missing_data_and_limitations', []))} Notes")
        critic = selected_report.get("critic_validation_results", {})
        st.markdown(f"**17. Critic Validation**: Valid=`{critic.get('valid', False)}` ({critic.get('passed_checks', 0)} checks)")
        st.markdown(f"**18. Final Status**: **`{selected_report.get('final_status')}`**")

    st.markdown("---")

    # Expandable JSON Viewer
    with st.expander("📄 View Complete Raw JSON Schema"):
        st.json(selected_report)
