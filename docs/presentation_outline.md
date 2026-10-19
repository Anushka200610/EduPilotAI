# EduPilot AI: CA-3 Presentation Outline (5-Minute Delivery Guide)

**Course**: Second-Year Undergraduate AIML Continuous Assessment 3 (CA-3)  
**Project**: EduPilot AI: An Agentic AI System for Student Performance Analysis and Academic Intervention  
**Team Details**:  
- Student 1 Name: `[YOUR NAME]` | PRN: `[YOUR PRN]`  
- Student 2 Name: `[PARTNER NAME]` | PRN: `[PARTNER PRN]`  
- Faculty Evaluator: `[FACULTY NAME]` | Department: `AIML / CSE`  
**Duration**: 5 Minutes (0:00 to 5:00)  

---

## Slide 1: Title & Project Overview (0:00 – 0:40)

- **Slide Title**: EduPilot AI: An Agentic AI System for Student Performance Analysis and Academic Intervention
- **Subtitle**: Second-Year Undergraduate AIML CA-3 Proof of Concept (Fall 2026)
- **Team Info**:
  - Presenter: `[YOUR NAME]` (PRN: `[YOUR PRN]`)
  - Team Partner: `[PARTNER NAME]` (PRN: `[PARTNER PRN]`)
  - Department of Artificial Intelligence & Machine Learning
- **Core Value Proposition**:
  - Automating early academic screening and multi-subject data cross-referencing.
  - Multi-agent orchestration via LangGraph, tool abstraction via MCP, and independent adversarial Critic validation.
  - Strict human-in-the-loop decision-support boundary.

### 🎙️ Speaker Notes (0:00 – 0:40):
> "Good morning, respected faculty and evaluators. Today, we are presenting EduPilot AI, an Agentic AI decision-support system designed to solve a critical challenge in academic institutions: timely, evidence-grounded student performance analysis and early intervention.
> Modern universities track attendance, continuous assessments, and assignments across separate portals. Manually cross-referencing these records across multiple subjects for 100 students takes hours and often delays intervention until it is too late. EduPilot AI automates this review using four specialized agents, transparent decision rules, and LangGraph orchestration."

---

## Slide 2: Problem Statement & Domain Justification (0:40 – 1:20)

- **Slide Title**: Problem Statement & Higher Education Domain Context
- **The Challenge**:
  - Scattered records across biometric logs, continuous assessment spreadsheets, and LMS submission folders.
  - Cognitive overload on faculty mentors managing 30–60 students per batch.
  - Delayed detection: Students falling behind or experiencing score drops often go unnoticed until formal mid-term failure.
- **Why Agentic AI?**:
  - Traditional scripts are rigid and black-box LLMs hallucinate calculations.
  - Multi-agent architecture separates planning, data analytics, intervention formulation, and independent adversarial auditing.
- **Key Invariants**:
  - Deterministic calculations: No paid API dependencies, 100% reproducible.
  - Explainability: Every finding links to verifiable numerical evidence.

### 🎙️ Speaker Notes (0:40 – 1:20):
> "In second-year engineering curricula, foundational courses like Data Structures and Machine Learning require continuous engagement. When a student's attendance slips below 75% or their exam score drops sharply, early detection is vital.
> However, existing manual audits are fragmented and slow. A simple hardcoded script cannot adapt its execution plan or audit itself, while a raw generative LLM might hallucinate numbers. By using an agentic multi-agent workflow, we decompose the review: the Planning Agent defines indicators, the Analytics Agent retrieves facts via MCP, the Intervention Agent designs recovery roadmaps, and the Critic independently audits all mathematical calculations."

---

## Slide 3: Existing Process vs. EduPilot AI Solution (1:20 – 2:00)

- **Slide Title**: Comparative Analysis: Existing Workflow vs. EduPilot AI
- **Comparison Matrix**:
  - **Data Aggregation**: Manual Excel consolidation (15–30 min/student) $\rightarrow$ Standardized MCP queries (< 10 ms).
  - **Pattern Recognition**: Isolated subject checks $\rightarrow$ Cross-subject correlation & trajectory detection.
  - **Validation**: Unverified manual notes $\rightarrow$ Independent Critic Agent recomputing invariants.
  - **Intervention Plan**: Subjective verbal advice $\rightarrow$ Standardized 18-field report with assigned roles & review periods.
- **Decision-Support Guardrail**:
  - EduPilot AI does not debar, penalize, or replace teachers. It delivers audit-ready intelligence to human mentors.

### 🎙️ Speaker Notes (1:20 – 2:00):
> "This slide illustrates the contrast. Instead of faculty spending 20 minutes manually inspecting spreadsheets for a single student, EduPilot AI executes end-to-end multi-agent screening in under 10 milliseconds.
> More importantly, our system introduces standardized intervention planning. Rather than vague verbal warnings, the system assigns a responsible faculty role, a concrete review timeline—such as two weeks—and a measurable milestone, such as attending 85% of upcoming classes or scoring above 50% in the next diagnostic test. And crucially, all recommendations require human faculty approval."

---

## Slide 4: AI Agent Taxonomy, Architecture & LangGraph Flow (2:00 – 2:50)

- **Slide Title**: AI Agent Taxonomy, LangGraph State Machine & MCP Integration
- **Russell & Norvig AI Agent Taxonomy Grounding**:
  1. **Agent 1: Goal-Based Agent (Academic Planning Agent)**: Decomposes high-level goal $G$ into an ordered 6-step plan and specifies academic indicator dependencies.
  2. **Agent 2: Model-Based Reflex Agent (Student Analytics Agent)**: Maintains internal longitudinal performance model across terms; fires condition-action reflex rules via MCP tools.
  3. **Agent 3: Utility-Based Agent (Intervention Planning Agent)**: Optimizes pedagogical recovery utility function $U(Action, Severity, Role)$ balancing recovery impact vs student/faculty burden.
  4. **Agent 4: Learning & Verification Agent (Critic & Auditor)**: Features an adversarial Critic element asserting invariants, feeding error signals to the Correction Node for bounded adaptive learning retries.
- **LangGraph State Machine**:
  - Typed shared state `EduPilotState`.
  - Conditional edge after input validation (routes invalid IDs directly to report generator).
  - Conditional edge after Critic validation (routes passed runs to report generator; routes discrepancies to correction node with bounded 2-retry limit).

### 🎙️ Speaker Notes (2:00 – 2:50):
> "Here is our core AIML theoretical grounding. In Stuart Russell and Peter Norvig's foundational framework, agents are classified by how they perceive and act. EduPilot AI maps each agent to an explicit paradigm:
> Agent 1 is a Goal-Based Agent that plans sub-goals to satisfy the review objective.
> Agent 2 is a Model-Based Reflex Agent maintaining an internal longitudinal model of student trajectories and executing condition-action rules through our standardized Model Context Protocol (MCP) server.
> Agent 3 is a Utility-Based Agent that maximizes a pedagogical recovery utility function, balancing intervention impact against student burden.
> And Agent 4 is a Learning & Verification Agent featuring an adversarial Critic element that verifies mathematical invariants and drives the correction learning loop. Orchestration is governed by a LangGraph state machine with bounded retries."

---

## Slide 5: Live Streamlit Dashboard Demonstration (2:50 – 3:45)

- **Slide Title**: Streamlit PoC Dashboard Demonstration
- **Key Modules Showcased**:
  - **Academic Overview**: Cohort-wide metrics across 100 synthetic students, Plotly histograms, and archetype distribution.
  - **Analyze Student**: Live single-student analysis showcasing indicators, attendance charts, score trajectories, and evidence callouts.
  - **Live Workflow Trace**: Real LangGraph node execution events, durations, and MCP tool call logs.
  - **Intervention Reports**: 18-field standardized documentation with JSON/CSV export.
  - **Batch Analysis**: Simultaneous section screening with priority categorization (High, Medium, Low).
- **Interactive Thresholds**: Real-time slider reconfiguration (e.g., adjusting attendance threshold from 75% to 80%).

### 🎙️ Speaker Notes (2:50 – 3:45):
> "Now let us view the live demonstration. Our Streamlit dashboard provides a clean, responsive academic portal.
> On the Analyze Student page, when we select student STU1016—who has attendance issues—and click Run Analysis, the LangGraph engine executes across all nodes in under 25 milliseconds.
> The UI displays the student's profile, overall attendance, and subject breakdown with an interactive 75% threshold line. Below, each identified concern is presented with verifiable evidence.
> Next, on the Agent Workflow page, faculty can inspect the actual LangGraph trace: every node name, its start time, latency in milliseconds, and the exact MCP tool invocations. This provides 100% observability—no hidden black-box decisions."

---

## Slide 6: Verification, Critic Audit & Evaluation Results (3:45 – 4:25)

- **Slide Title**: Verification, Critic Audit & Empirical Benchmark Results
- **Automated Testing**:
  - Comprehensive Pytest suite across 26 test cases: 100% pass rate.
  - Tests data schemas, decision rules, agent behaviors, LangGraph routing, and MCP tools.
- **Empirical Benchmarks (`scripts/evaluate.py`)**:
  - 10 reproducible benchmark scenarios evaluated.
  - **100.0% Rule Compliance Rate** across all synthetic archetypes.
  - Average execution latency: **6.9 milliseconds**.
  - 100% trap rate for corrupt data invariants ($attended > held$) and ungrounded claims.

### 🎙️ Speaker Notes (3:45 – 4:25):
> "Technical correctness and safety are the core priorities of this project. We built an automated test suite of 26 pytest unit tests covering data schemas, invariant checks, and graph transitions—all 26 pass.
> Furthermore, our evaluation script benchmarks 10 reproducible scenarios, including high performers, low attendance, failing marks, declining test scores, missing data, and corrupt records. Across all scenarios, EduPilot AI achieves a 100% rule-compliance rate with an average latency of only 6.9 milliseconds.
> The Critic Agent successfully trapped intentional adversarial attacks, such as impossible attendance values or ungrounded claims, ensuring that no unverified report is ever marked VALIDATED."

---

## Slide 7: Limitations, Ethical Governance & Conclusion (4:25 – 5:00)

- **Slide Title**: Ethical Safeguards, Limitations & Conclusion
- **Ethical Safeguards**:
  - Strict decision support: Never makes consequential or punitive decisions automatically.
  - Privacy by design: Anonymous synthetic identifiers (`STU####`); zero PII.
  - Fairness: Evaluates academic variables only; zero demographic bias.
- **Honest Limitations**:
  - Evaluated on synthetic distributions; real classrooms have complex socio-emotional factors.
  - Qualitative context (medical leave, family emergencies) requires human teacher appraisal.
- **Conclusion**:
  - EduPilot AI demonstrates that Agentic AI with LangGraph and MCP can provide reliable, transparent, and instantaneous decision support to educators.

### 🎙️ Speaker Notes (4:25 – 5:00):
> "To conclude, EduPilot AI demonstrates how agentic AI can assist educators ethically. We honestly acknowledge its limitations: the system was built and tested on synthetic data, and numerical records cannot capture personal emergencies or illness. Therefore, human-in-the-loop oversight is mandatory.
> By uniting LangGraph orchestration, standardized MCP data tools, deterministic rules, and an independent Critic Agent, EduPilot AI provides a production-grade, demonstrable blueprint for modern educational decision support.
> Thank you, and we welcome your questions!"
