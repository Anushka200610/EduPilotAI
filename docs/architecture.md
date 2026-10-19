# EduPilot AI: Architecture Specification & System Design

This document details the multi-agent system architecture, data flow, tool interfaces,
and orchestration state machine implemented in **EduPilot AI**.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    %% User & Presentation Layer
    User(["Faculty Mentor / Advisor"])
    UI["Streamlit Interactive Dashboard (app.py)"]
    User <-->|Select Student & View Reports| UI

    %% Orchestration & State Layer
    subgraph LangGraphOrchestrator["LangGraph State Machine Engine (orchestration/graph.py)"]
        State[("Typed Shared State: EduPilotState")]
        
        IV["Node 1: Input Validation"]
        PlanAgent["Node 2: Academic Planning Agent (agents/planner_agent.py)"]
        AnalyticsAgent["Node 3: Student Analytics Agent (agents/analytics_agent.py)"]
        IntervAgent["Node 4: Intervention Planning Agent (agents/intervention_agent.py)"]
        CriticAgent["Node 5: Critic & Validation Agent (agents/critic_agent.py)"]
        CorrectionNode["Node 6: Correction / Recalculation Node"]
        ReportGenNode["Node 7: Report Generator Node (tools/report_tools.py)"]
    end

    UI -->|Invoke Workflow| IV
    IV -->|State Check| State
    IV -->|Valid ID| PlanAgent
    IV -->|Invalid ID| ReportGenNode
    
    PlanAgent -->|Formulate 6-Step Plan| AnalyticsAgent
    AnalyticsAgent -->|Populate Indicators & Evidence| IntervAgent
    IntervAgent -->|Propose Interventions| CriticAgent
    
    %% Conditional Routing from Critic
    CriticAgent -->|Pass: All Checks OK| ReportGenNode
    CriticAgent -->|Fail: Discrepancy & Retry < 2| CorrectionNode
    CorrectionNode -->|Re-sync & Loop Back| AnalyticsAgent
    CriticAgent -->|Fail: Retry Exhausted| ReportGenNode

    %% Tool Layer: MCP
    subgraph MCPLayer["Model Context Protocol (MCP 2.x Layer)"]
        MCPClient["EduPilot MCP Client (mcp_server/client.py)"]
        MCPServer["Local Academic MCP Server (mcp_server/server.py)"]
        
        subgraph ExposedAcademicTools["7 Standard Academic MCP Tools"]
            T1["get_student_profile"]
            T2["get_attendance_history"]
            T3["get_assessment_results"]
            T4["get_assignment_status"]
            T5["calculate_attendance"]
            T6["calculate_academic_indicators"]
            T7["validate_intervention_plan"]
        end
    end

    AnalyticsAgent <-->|Async/Sync Invocation| MCPClient
    MCPClient <-->|stdio / in-process MCP protocol| MCPServer
    MCPServer --- ExposedAcademicTools

    %% Rules & Data Layer
    subgraph DataAndRulesLayer["Data & Decision Engine"]
        Rules["Deterministic Decision Rules Engine (tools/decision_rules.py)"]
        Config["Configurable Thresholds (config/settings.py)"]
        DataSvc["Data Service (services/data_service.py)"]
        
        subgraph SyntheticDataStore["Synthetic Datasets (Seed=42)"]
            CSV1[("students.csv")]
            CSV2[("attendance.csv")]
            CSV3[("assessments.csv")]
            CSV4[("assignments.csv")]
        end
    end

    ExposedAcademicTools <--> DataSvc
    ExposedAcademicTools <--> Rules
    Rules <--> Config
    DataSvc <--> SyntheticDataStore

    %% Output
    ReportGenNode -->|Standardized 18-Field Report| FinalReport[("Final Academic Intervention Report")]
    FinalReport --> UI
```

---

## 2. Theoretical Grounding: Russell & Norvig AI Agent Taxonomy

EduPilot AI grounds its multi-agent architecture in the classical taxonomy defined by Stuart Russell and Peter Norvig (*Artificial Intelligence: A Modern Approach*, 4th Edition, Chapter 2). Each agent embodies a distinct theoretical agent paradigm:

| Agent | Taxonomy Classification | Theoretical Mechanism | PEAS Sensor / Actuator Profile |
| :--- | :--- | :--- | :--- |
| **Agent 1: Academic Planning Agent** | **Goal-Based Agent** | Combines goal descriptions $G = \text{Objective}(\text{Student ID})$ with action predictions to formulate an ordered 6-step plan and indicator dependencies. | **S**: Student ID, Objective<br/>**A**: Ordered 6-step plan in shared state |
| **Agent 2: Student Analytics Agent** | **Model-Based Reflex Agent** | Maintains internal longitudinal state across sequential assessments and fires condition-action reflex rules ($P \to A$). | **S**: Academic MCP tool JSON payloads<br/>**A**: Indicators, concerns, evidence |
| **Agent 3: Intervention Planning Agent** | **Utility-Based Agent** | Maximizes pedagogical recovery utility function $U(A, S, R)$ to trade off intervention intensity against student and faculty burden. | **S**: Flagged concerns & evidence<br/>**A**: Prioritized intervention roadmaps |
| **Agent 4: Critic & Validation Agent** | **Learning & Verification Agent** | Features a distinct Critic component asserting invariants, generating error signals that trigger the Correction Node for bounded retries. | **S**: Recomputed values, raw data assertions<br/>**A**: Verification status, routing signal |

---

## 3. Sequence Diagram: Single Student Academic Investigation

The following sequence diagram illustrates the lifecycle of analyzing a student (e.g., `STU1016`):

```mermaid
sequenceDiagram
    autonumber
    actor Faculty as Faculty Mentor
    participant UI as Streamlit UI
    participant Graph as LangGraph Engine
    participant Planner as Planning Agent
    participant Analytics as Analytics Agent
    participant MCP as MCP Client & Server
    participant Rules as Decision Rules Engine
    participant Interv as Intervention Agent
    participant Critic as Critic Agent
    participant Report as Report Generator

    Faculty->>UI: Select Student STU1016 and Click "Run Analysis"
    UI->>Graph: invoke(initial_state: {student_id: "STU1016"})
    
    %% Input Validation
    Graph->>Graph: node_input_validation()
    Note over Graph: Check format STU#### and registry existence
    
    %% Planning Agent
    Graph->>Planner: node_academic_planner()
    Planner-->>Graph: execution_plan (6 steps, required tools, expected outputs)
    
    %% Analytics Agent & MCP
    Graph->>Analytics: node_student_analytics()
    Analytics->>MCP: call_tool("calculate_academic_indicators", {student_id: "STU1016"})
    MCP->>Rules: evaluate_attendance(), evaluate_assessments(), evaluate_assignments()
    Rules-->>MCP: indicators + flagged concerns + evidence
    MCP-->>Analytics: structured indicators dict (Telemetry logged)
    Analytics-->>Graph: state.indicators, state.concerns, state.evidence
    
    %% Intervention Agent
    Graph->>Interv: node_intervention_planner()
    Interv->>Interv: Map concerns to actions, roles, review periods, measurable goals
    Interv-->>Graph: state.interventions (Prioritized action plan)
    
    %% Critic Agent
    Graph->>Critic: node_critic_validation()
    Critic->>Critic: Recompute attendance % and marks % independently
    Critic->>Critic: Verify mathematical invariants (attended <= held, 0 <= marks <= max)
    Critic->>Critic: Check threshold fidelity (no false positives / false negatives)
    Critic->>MCP: call_tool("validate_intervention_plan", {interventions, indicators})
    MCP-->>Critic: validation_result {valid: True, errors: []}
    Critic-->>Graph: state.validation_results, validation_passed = True
    
    %% Conditional Edge
    Graph->>Graph: route_after_critic() -> returns "report_generator"
    
    %% Report Generator
    Graph->>Report: node_report_generator()
    Report->>Report: Compile 18-field standardized report (Status: VALIDATED)
    Report-->>Graph: state.final_report, status = "COMPLETED"
    
    Graph-->>UI: Return final state with complete execution trace
    UI-->>Faculty: Render academic indicators, Plotly charts, concerns, interventions, and audit trail
```

---

## 3. Shared State Schema (`EduPilotState`)

The shared state passed through all nodes is strictly typed as follows:

```python
class EduPilotState(TypedDict):
    request_id: str
    student_id: str
    batch_ids: Optional[List[str]]
    analysis_mode: str  # "single" | "batch"
    analysis_objective: str

    execution_plan: Dict[str, Any]       # Steps generated by Planning Agent
    profile: Dict[str, Any]              # Student metadata
    indicators: Dict[str, Any]           # Calculated attendance, marks, assignments
    concerns: List[Dict[str, Any]]       # Concerns flagged by decision rules
    evidence: Dict[str, Any]             # Traceable numerical findings
    support_priority: str                # HIGH | MEDIUM | LOW | NONE

    interventions: List[Dict[str, Any]]  # Actions, roles, review periods, goals
    validation_results: Dict[str, Any]   # Critic verification report
    validation_passed: bool              # Critic pass/fail boolean flag
    retry_count: int                     # Active correction retry counter
    max_retries: int                     # Bounded limit (default 2)

    execution_trace: List[Dict[str, Any]] # Audit event log per node
    mcp_tool_calls: List[Dict[str, Any]]  # Telemetry log of MCP tool invocations
    final_report: Dict[str, Any]         # Standard 18-field report
    status: str                          # Workflow lifecycle status
    errors: List[str]                    # Trapped error messages
```

---

## 4. MCP Communication Architecture

The Model Context Protocol establishes a clean client-server architecture:
- **Server (`mcp_server/server.py`)**: Built on `mcp.server.mcpserver.MCPServer`. Standardizes data retrieval and calculation tools into registered tool schemas with defined inputs and JSON outputs.
- **Client (`mcp_server/client.py`)**: The `EduPilotMCPClient` provides both synchronous and asynchronous invocations, validates arguments, logs duration (latency in milliseconds), logs status (`SUCCESS` / `ERROR`), and records summary previews for execution traceability.
- **Standalone Transport**: The MCP server can also be launched independently via standard I/O:
  ```powershell
  py -m mcp_server.server
  ```
  allowing any external MCP-compliant host to query EduPilot academic tools.
