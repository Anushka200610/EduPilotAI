"""Synthetic Data Generator for EduPilot AI.

Generates 100 realistic, synthetic student records across 4 CSV files:
- data/students.csv
- data/attendance.csv
- data/assessments.csv
- data/assignments.csv

Includes reproducible archetypes for academic evaluation:
1. Strong Academic Performance
2. Low Attendance (<75%)
3. Low Subject Performance (<40%)
4. Declining Assessment Results
5. Missing Assignments
6. Multiple Simultaneous Concerns
7. Typical/Average Performance
8. Incomplete/Missing Records

All records are completely synthetic and generated using a deterministic random seed.
"""

import json
import random
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from config.settings import DATA_DIR, settings

# Subjects definition
SUBJECTS = [
    {"subject_id": "CS201", "name": "Data Structures & Algorithms", "faculty": "Dr. Ramesh Sharma"},
    {"subject_id": "CS202", "name": "Operating Systems", "faculty": "Prof. Anita Sen"},
    {"subject_id": "AI201", "name": "Machine Learning Foundations", "faculty": "Dr. Vikas Verma"},
    {"subject_id": "MATH201", "name": "Linear Algebra & Probability", "faculty": "Dr. Preeti Nair"},
]

PROGRAMS = ["B.Tech AIML", "B.Tech CSE", "B.Tech Data Science"]
SECTIONS = ["A", "B", "C"]
ACADEMIC_TERM = settings.academic_term
NUM_STUDENTS = 100


def generate_synthetic_data(seed: int = 42, output_dir: Path = DATA_DIR):
    """Generate all synthetic academic records reproducibly."""
    random.seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    students = []
    attendance = []
    assessments = []
    assignments = []
    scenarios_meta = {}

    student_ids = [f"STU{1000 + i}" for i in range(1, NUM_STUDENTS + 1)]

    # Categorize students into archetypes
    # 1. Strong: STU1001-STU1015 (15)
    # 2. Low attendance: STU1016-STU1025 (10)
    # 3. Low subject marks: STU1026-STU1035 (10)
    # 4. Declining results: STU1036-STU1045 (10)
    # 5. Missing assignments: STU1046-STU1055 (10)
    # 6. Multiple concerns: STU1056-STU1065 (10)
    # 7. Typical/Average: STU1066-STU1095 (30)
    # 8. Incomplete records: STU1096-STU1100 (5)

    for i, stu_id in enumerate(student_ids):
        # Student demographic/profile
        program = PROGRAMS[i % len(PROGRAMS)]
        section = SECTIONS[i % len(SECTIONS)]
        semester = 4

        students.append({
            "student_id": stu_id,
            "program": program,
            "semester": semester,
            "section": section,
            "academic_term": ACADEMIC_TERM,
            "synthetic_label": "Synthetic Record - Anonymous",
        })

        # Archetype determination
        idx = i + 1  # 1-indexed (1 to 100)

        if 1 <= idx <= 15:
            archetype = "STRONG_PERFORMANCE"
            desc = "Strong performer with >85% attendance, >75% marks, all assignments submitted."
        elif 16 <= idx <= 25:
            archetype = "LOW_ATTENDANCE"
            desc = "Attendance concern (<75%) in one or more subjects, standard performance."
        elif 26 <= idx <= 35:
            archetype = "LOW_SUBJECT_MARKS"
            desc = "Low marks (<40%) in one or more subjects despite adequate attendance."
        elif 36 <= idx <= 45:
            archetype = "DECLINING_PERFORMANCE"
            desc = "Steep drop in score (>=15% points) from Quiz 1 to Mid-Term Exam."
        elif 46 <= idx <= 55:
            archetype = "MISSING_ASSIGNMENTS"
            desc = "Multiple missing/overdue assignments despite acceptable exam scores."
        elif 56 <= idx <= 65:
            archetype = "MULTIPLE_CONCERNS"
            desc = "Simultaneous low attendance, failing marks, and missing assignments."
        elif 66 <= idx <= 95:
            archetype = "TYPICAL_AVERAGE"
            desc = "Regular student with average attendance (76-88%) and marks (55-75%)."
        else:
            archetype = "INCOMPLETE_DATA"
            desc = "Intentionally missing records (e.g. no attendance or missing exam entries) to test edge cases."

        scenarios_meta[stu_id] = {
            "student_id": stu_id,
            "archetype": archetype,
            "description": desc,
            "program": program,
            "section": section,
        }

        # Subject-level data generation
        for subj in SUBJECTS:
            subj_id = subj["subject_id"]

            # Edge case handling for Archetype 8 (Incomplete Data)
            if archetype == "INCOMPLETE_DATA":
                if stu_id == "STU1096":
                    # Missing all attendance
                    pass
                elif stu_id == "STU1097":
                    # Missing all assessments
                    pass
                elif stu_id == "STU1098" and subj_id in ["CS201", "AI201"]:
                    # Partial subject records missing
                    continue
                elif stu_id == "STU1099":
                    # Missing assignments completely
                    pass
                elif stu_id == "STU1100" and subj_id == "MATH201":
                    continue

            # 1. ATTENDANCE
            classes_held = random.choice([36, 40, 42])

            if archetype == "INCOMPLETE_DATA" and stu_id == "STU1096":
                # Skip attendance
                pass
            else:
                if archetype == "STRONG_PERFORMANCE":
                    attendance_rate = random.uniform(0.88, 0.98)
                elif archetype == "LOW_ATTENDANCE":
                    # Subj CS201 or AI201 has low attendance
                    attendance_rate = random.uniform(0.55, 0.71) if subj_id in ["CS201", "CS202"] else random.uniform(0.78, 0.88)
                elif archetype == "MULTIPLE_CONCERNS":
                    attendance_rate = random.uniform(0.50, 0.68)
                elif archetype == "TYPICAL_AVERAGE":
                    attendance_rate = random.uniform(0.76, 0.89)
                else:
                    attendance_rate = random.uniform(0.78, 0.92)

                classes_attended = int(round(classes_held * attendance_rate))
                # Invariant: classes_attended <= classes_held
                classes_attended = min(classes_attended, classes_held)
                classes_attended = max(0, classes_attended)

                attendance.append({
                    "student_id": stu_id,
                    "subject_id": subj_id,
                    "classes_held": classes_held,
                    "classes_attended": classes_attended,
                    "academic_term": ACADEMIC_TERM,
                })

            # 2. ASSESSMENTS
            # We generate two sequential assessments per subject:
            # - Quiz 1 (Max: 20 marks, Date: 2026-08-25)
            # - Mid-Term Exam (Max: 50 marks, Date: 2026-10-05)
            if archetype == "INCOMPLETE_DATA" and stu_id == "STU1097":
                # Skip assessments
                pass
            else:
                if archetype == "STRONG_PERFORMANCE":
                    q1_pct = random.uniform(0.80, 0.95)
                    mid_pct = random.uniform(0.82, 0.96)
                elif archetype == "LOW_SUBJECT_MARKS":
                    # Struggling in CS201 and AI201 (<40%)
                    if subj_id in ["CS201", "AI201"]:
                        q1_pct = random.uniform(0.20, 0.38)
                        mid_pct = random.uniform(0.25, 0.36)
                    else:
                        q1_pct = random.uniform(0.65, 0.78)
                        mid_pct = random.uniform(0.60, 0.75)
                elif archetype == "DECLINING_PERFORMANCE":
                    # Started high (75-88%), dropped significantly (by >= 20%) to (35-50%)
                    q1_pct = random.uniform(0.78, 0.88)
                    mid_pct = q1_pct - random.uniform(0.22, 0.32)
                elif archetype == "MULTIPLE_CONCERNS":
                    q1_pct = random.uniform(0.25, 0.42)
                    mid_pct = random.uniform(0.20, 0.38)
                else:
                    q1_pct = random.uniform(0.55, 0.75)
                    mid_pct = random.uniform(0.52, 0.74)

                q1_marks = round(20 * q1_pct, 1)
                mid_marks = round(50 * mid_pct, 1)

                # Clamp marks to [0, max_marks]
                q1_marks = max(0.0, min(20.0, q1_marks))
                mid_marks = max(0.0, min(50.0, mid_marks))

                assessments.append({
                    "student_id": stu_id,
                    "subject_id": subj_id,
                    "assessment_name": "Quiz 1",
                    "maximum_marks": 20.0,
                    "marks_obtained": q1_marks,
                    "assessment_date": "2026-08-25",
                })
                assessments.append({
                    "student_id": stu_id,
                    "subject_id": subj_id,
                    "assessment_name": "Mid-Term Exam",
                    "maximum_marks": 50.0,
                    "marks_obtained": mid_marks,
                    "assessment_date": "2026-10-05",
                })

            # 3. ASSIGNMENTS
            # 2 assignments per subject
            if archetype == "INCOMPLETE_DATA" and stu_id == "STU1099":
                # Skip assignments
                pass
            else:
                for a_idx, due_date in [(1, "2026-09-01"), (2, "2026-09-28")]:
                    asg_id = f"{subj_id}_A{a_idx}"
                    if archetype == "STRONG_PERFORMANCE":
                        status = "SUBMITTED"
                    elif archetype == "MISSING_ASSIGNMENTS":
                        # Deliberate missing assignments
                        status = "MISSING" if (subj_id in ["CS201", "CS202"] or a_idx == 2) else "SUBMITTED"
                    elif archetype == "MULTIPLE_CONCERNS":
                        status = random.choice(["MISSING", "LATE", "MISSING"])
                    elif archetype == "LOW_ATTENDANCE":
                        status = random.choice(["SUBMITTED", "SUBMITTED", "LATE"])
                    else:
                        status = random.choices(["SUBMITTED", "LATE", "MISSING"], weights=[80, 15, 5])[0]

                    assignments.append({
                        "student_id": stu_id,
                        "subject_id": subj_id,
                        "assignment_id": asg_id,
                        "submission_status": status,
                        "due_date": due_date,
                    })

    # Convert to DataFrames and Save
    df_students = pd.DataFrame(students)
    df_attendance = pd.DataFrame(attendance)
    df_assessments = pd.DataFrame(assessments)
    df_assignments = pd.DataFrame(assignments)

    df_students.to_csv(output_dir / "students.csv", index=False)
    df_attendance.to_csv(output_dir / "attendance.csv", index=False)
    df_assessments.to_csv(output_dir / "assessments.csv", index=False)
    df_assignments.to_csv(output_dir / "assignments.csv", index=False)

    with open(output_dir / "scenarios_meta.json", "w", encoding="utf-8") as f:
        json.dump(scenarios_meta, f, indent=2)

    print(f"[OK] Generated {len(df_students)} students in {output_dir}")
    print(f"[OK] Generated {len(df_attendance)} attendance records")
    print(f"[OK] Generated {len(df_assessments)} assessment records")
    print(f"[OK] Generated {len(df_assignments)} assignment records")
    print(f"[OK] Saved scenarios metadata to {output_dir / 'scenarios_meta.json'}")


if __name__ == "__main__":
    generate_synthetic_data()
