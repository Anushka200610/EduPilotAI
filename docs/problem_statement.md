# EduPilot AI: Problem Statement & Academic Justification

**Project Title**: EduPilot AI: An Agentic AI System for Student Performance Analysis and Academic Intervention  
**Course**: Second-Year Undergraduate Artificial Intelligence & Machine Learning (AIML)  
**Assignment**: Continuous Assessment 3 (CA-3)  
**Academic Term**: Fall 2026  
**Domain**: Higher Education Learning Analytics & Decision Support Systems  

---

## 1. Background & Context

Modern engineering universities and degree-granting institutions maintain student records across distinct, siloed repositories:
- Daily or weekly classroom attendance records (typically managed via biometric portals or faculty register uploads).
- Formative and summative assessment marks (quizzes, lab evaluations, continuous assessments, and mid-term exam sheets).
- Coursework and laboratory assignment submissions (managed through disparate Learning Management Systems such as Moodle, Canvas, or Google Classroom).

In undergraduate technical education—especially during intensive second-year curricula featuring foundational computer science and machine learning coursework (e.g., Data Structures, Operating Systems, Machine Learning Foundations, Linear Algebra)—early identification of students encountering academic challenges is paramount.

---

## 2. The Existing Academic Review Process

In most contemporary academic institutions, the review workflow is manual, fragmented, and reactive:
1. Faculty members and course coordinators compile attendance registers at mandatory intervals (e.g., monthly or just before mid-term examinations).
2. Faculty individually record quiz and mid-term scores in departmental spreadsheets.
3. Class coordinators and mentors cross-reference attendance against examination performance manually.
4. Faculty advisors conduct one-on-one reviews only after mid-term grades are formally submitted.

### Inefficiencies and Pain Points in the Existing Process

- **Fragmented Data Cross-Referencing**: Analyzing a single student requires inspecting at least three distinct documents across four to six subjects. For a class of 60 to 100 students, comprehensive manual cross-referencing demands hours of administrative effort.
- **Delayed Intervention**: Because manual audits are time-consuming, interventions typically occur late in the semester (e.g., weeks 8–10), leaving insufficient time for remedial instruction or attendance recovery before final examinations.
- **Cognitive Overload and Human Error**: Tiring manual reviews increase the likelihood of missing students with subtle warning signs (such as a steep 20% score drop between Quiz 1 and Mid-Term despite passing marks, or isolated attendance problems in one critical subject).
- **Inconsistent Support Plans**: Without standardized intervention protocols, recommendations vary drastically between faculty members, frequently omitting concrete timelines, assigned roles, or measurable follow-up goals.

---

## 3. Proposed Solution: EduPilot AI

EduPilot AI introduces an autonomous, multi-agent decision-support framework designed to assist faculty mentors. The system analyzes synthetic student academic records, calculates attendance and performance indicators, flags concerns using configurable rules, formulates tailored intervention roadmaps, validates all findings through an independent Critic Agent, and generates standardized 18-field reports for human review.

### Why Agentic AI? (Justification for Multi-Agent Architecture)

Traditional monolithic scripts or standard rule evaluation engines cannot dynamically adapt their execution plan, trace cross-domain evidence across multiple tools, or adversarially audit their own calculations. EduPilot AI solves this through a multi-agent paradigm:

1. **Separation of Cognitive Concerns**:
   - The **Planning Agent** determines which specific indicators and tools are required for each student.
   - The **Analytics Agent** queries standardized **MCP tools** to compute indicators and gather traceable evidence.
   - The **Intervention Agent** translates concerns into pedagogically sound recovery plans with assigned roles and review periods.
   - The **Critic Agent** functions as an independent verification auditor, recomputing calculations and verifying invariants before finalizing reports.
2. **Standardized Tool Interoperability via MCP**:
   - Data access is mediated through the **Model Context Protocol (MCP)**, decoupling agents from underlying database implementations and preparing the architecture for enterprise LMS integration.
3. **Graph-Controlled Execution via LangGraph**:
   - LangGraph provides cyclic state management, conditional routing (e.g., routing invalid input away from analysis nodes, or routing validation failures to a correction node), and bounded retries.
4. **Adversarial Self-Correction**:
   - The independent Critic prevents hallucinations, catches false positives/negatives, and enforces data invariants ($attended \le held$, $0 \le marks \le max$).

---

## 4. Project Objectives

1. **Automate Comprehensive Review**: Ingest and analyze attendance, assessment scores, and assignment submissions across multiple subjects within milliseconds per student.
2. **Transparent Decision Rules**: Eliminate black-box unpredictability by relying on configurable, deterministic formulas and transparent thresholds.
3. **Traceable Evidence Mapping**: Guarantee that every flagged concern links directly to verifiable numerical facts in synthetic records.
4. **Pedagogically Actionable Interventions**: Provide structured recommendations specifying the action, responsible faculty role, suggested review window, and measurable outcome.
5. **Rigorous Verification via Critic Agent**: Independently recompute all mathematical metrics and verify intervention grounding prior to report dispatch.
6. **Faculty Dashboard**: Provide a polished Streamlit interface with Plotly visualizations, live LangGraph execution tracing, batch processing, and 18-field report export.

---

## 5. Scope & Decision-Support Boundaries

> **IMPORTANT ETHICAL BOUNDARY**:  
> EduPilot AI is strictly a **decision-support proof-of-concept**. It is intentionally designed **never** to make consequential or punitive academic decisions automatically. The system does not assign final grades, impose disciplinary actions, issue debarment notices, or replace human faculty judgment. All generated intervention plans require review, contextual evaluation, and approval by human academic advisors.
