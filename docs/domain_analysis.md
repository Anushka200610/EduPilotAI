# EduPilot AI: Domain Analysis & Workflow Engineering

**Domain**: Higher Education Academic Advisement & Early Intervention  
**Target Stakeholders**: Faculty Mentors, Course Instructors, Class Coordinators, Heads of Department  

---

## 1. Academic Review Workflows in Higher Education

Academic advisement in technical universities operates as a multi-tier governance model:

```
[University Academic Council]
         │
[Department Head / Dean]
         │
[Class Coordinator / Year Mentor]
         │
[Course Faculty & Lab Instructors]
         │
[Individual Student]
```

### Key Responsibilities by Academic Role

1. **Course Instructor**:
   - Maintains continuous classroom attendance and lab session participation.
   - Evaluates formative continuous assessments, quizzes, and assignments.
   - Responsible for detecting topic-specific conceptual difficulties (e.g., student struggling in *Dynamic Programming* in CS201).

2. **Faculty Mentor / Class Coordinator**:
   - Oversees holistic progress across all enrolled subjects for an assigned batch (typically 20–30 students).
   - Responsible for identifying systemic attendance issues across multiple subjects.
   - Acts as the primary point of contact for student counseling and parental advisement.

3. **Academic Advisor / Department Head**:
   - Reviews students facing multiple simultaneous academic concerns.
   - Approves special remedial sessions, makeup evaluation requests, or extended academic probation agreements.

---

## 2. Limitations of Manual Review Workflows

| Characteristic | Manual Academic Review | EduPilot AI Framework |
| :--- | :--- | :--- |
| **Review Frequency** | Infrequent (monthly or once per mid-term). | Continuous and on-demand (instant execution). |
| **Data Aggregation** | Scattered across physical registers, Excel sheets, LMS exports. | Unified, standardized data ingestion via MCP tools. |
| **Cross-Subject Correlation**| Difficult; faculty rarely inspect performance in other subjects. | Holistic cross-subject analysis across all enrolled courses. |
| **Trajectory Detection** | Difficult to calculate score drop between quizzes and mid-terms manually. | Automated trajectory detection (flagging score drops $\ge 15\%$ pts). |
| **Action Plan Consistency** | Subjective; lacks standardized timelines and measurable goals. | Structured 18-field standardized reports with explicit roles & outcomes. |
| **Execution Latency** | 15–30 minutes per student across multiple registers. | Under 10 milliseconds per student. |

---

## 3. Automated vs. Human-Controlled Responsibilities

To guarantee safety, ethics, and compliance with academic governance policies, EduPilot AI explicitly delineates between tasks that are automated and tasks that remain strictly under human control:

### Fully Automated Tasks (By EduPilot AI Agents)
- Ingesting attendance, assessment marks, and assignment status records.
- Calculating attendance percentages: $\frac{\text{Attended}}{\text{Held}} \times 100$.
- Calculating assessment percentages: $\frac{\text{Obtained}}{\text{Max}} \times 100$.
- Computing sequential score deltas: $\text{Score}_1 - \text{Score}_2$.
- Comparing metrics against transparent, configurable thresholds.
- Cross-referencing identified concerns with synthetic data facts to assemble verifiable evidence.
- Formulating draft intervention roadmaps with suggested roles and timelines.
- Adversarially auditing calculations and invariant bounds via the Critic Agent.
- Compiling standardized 18-field JSON and CSV reports.

### Strictly Human-Controlled Tasks (By Faculty & Academic Mentors)
- **Contextual Appraisal**: Evaluating extenuating life circumstances (illness, bereavement, family emergencies, approved sports or extracurricular leave) that are absent from raw spreadsheets.
- **Intervention Approval**: Reviewing, modifying, and officially signing off on proposed intervention roadmaps before any formal communication.
- **Direct Student Counseling**: Conducting compassionate, one-on-one counseling discussions with the student.
- **Consequential Decisions**: Determining academic eligibility, granting attendance relaxations, or imposing remedial requirements.
- **Pedagogical Action**: Designing and conducting targeted makeup tutorials, review sessions, or re-tests.
