"""Architecture Diagram PNG Generator for EduPilot AI.

Generates a publication-quality, 300 DPI architecture diagram PNG
with clean layout, anti-aliased geometry, and clear contrast.

Output: docs/architecture.png
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from config.settings import DOCS_DIR


def generate_architecture_png(output_path: Path = DOCS_DIR / "architecture.png"):
    # High-resolution figure: 22 x 14 inches at 300 DPI = 6600 x 4200 px
    fig, ax = plt.subplots(figsize=(22, 14), dpi=300)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # -------------------------------------------------------------------------
    # 0. Header & Branding Banner
    # -------------------------------------------------------------------------
    banner = FancyBboxPatch(
        (2, 91.5), 96, 7.0,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        facecolor="#0F172A", edgecolor="#0284C7", linewidth=2.0,
    )
    ax.add_patch(banner)

    ax.text(
        4, 95.8, "EduPilot AI — Multi-Agent System Architecture",
        fontsize=22, fontweight="bold", color="#FFFFFF", va="center"
    )
    ax.text(
        4, 93.2, "AI Agent Taxonomy: Goal, Reflex, Utility & Learning  •  LangGraph State Machine  •  Model Context Protocol (MCP 2.x)  •  Adversarial Critic Audit",
        fontsize=12, color="#94A3B8", va="center"
    )
    ax.text(
        96, 94.5, "Second-Year AIML CA-3 PoC\nPython 3.11 / 3.13  •  Seed = 42",
        fontsize=11, color="#38BDF8", ha="right", va="center", fontweight="bold"
    )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def draw_container(x, y, w, h, title, subtitle, bg_color, border_color):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.0",
            facecolor=bg_color, edgecolor=border_color, linewidth=2.0, linestyle="--"
        )
        ax.add_patch(box)
        # Title badge
        badge_w = max(len(title) * 0.52 + 1.8, 12.0)
        tag = FancyBboxPatch(
            (x + 1.2, y + h - 2.8), badge_w, 2.4,
            boxstyle="round,pad=0.3,rounding_size=0.5",
            facecolor=border_color, edgecolor="none"
        )
        ax.add_patch(tag)
        ax.text(x + 2.0, y + h - 1.6, title, fontsize=10.5, fontweight="bold", color="#FFFFFF", va="center")
        if subtitle:
            ax.text(x + badge_w + 2.5, y + h - 1.6, f"({subtitle})", fontsize=10, color="#64748B", va="center", style="italic")

    def draw_node(x, y, w, h, title, desc, tag_text, bg_color, border_color, text_color="#0F172A"):
        card = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.4,rounding_size=0.7",
            facecolor=bg_color, edgecolor=border_color, linewidth=1.5,
            alpha=0.98
        )
        ax.add_patch(card)
        ax.text(x + 1.2, y + h - 1.5, title, fontsize=11, fontweight="bold", color=text_color, va="center")
        if tag_text:
            tag_w = max(len(tag_text) * 0.48 + 1.2, 5.0)
            t_box = FancyBboxPatch(
                (x + w - 0.8 - tag_w, y + h - 2.1), tag_w, 1.3,
                boxstyle="round,pad=0.15,rounding_size=0.3",
                facecolor=border_color, edgecolor="none"
            )
            ax.add_patch(t_box)
            ax.text(x + w - 0.8 - (tag_w / 2), y + h - 1.45, tag_text, fontsize=8, color="#FFFFFF", ha="center", va="center", fontweight="bold")
        if desc:
            ax.text(x + 1.2, y + 1.0, desc, fontsize=8.5, color="#334155", va="bottom", wrap=True)

    def draw_arrow(start, end, label=None, color="#2563EB", rad=0.0, lw=2.0, ls="-"):
        arrow = FancyArrowPatch(
            start, end,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=6,head_width=4",
            color=color, linewidth=lw, linestyle=ls,
            zorder=5
        )
        ax.add_patch(arrow)
        if label:
            mx = (start[0] + end[0]) / 2 + (rad * 4)
            my = (start[1] + end[1]) / 2
            ax.text(
                mx, my, label,
                fontsize=8.5, color=color, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor=color, alpha=0.95, lw=1.0),
                zorder=6
            )

    # -------------------------------------------------------------------------
    # CONTAINER 1: User & Presentation Layer (Top Left)
    # -------------------------------------------------------------------------
    draw_container(2, 57, 24, 32, "LAYER 1: USER & PRESENTATION", "Streamlit Multi-Page UI", "#F8FAFC", "#0284C7")

    draw_node(
        3.5, 75.5, 21, 9.5,
        "Faculty Mentor / Evaluator",
        "Selects student ID (e.g. STU1016),\nconfigures thresholds via sliders,\nand triggers multi-agent review.",
        "HUMAN IN THE LOOP", "#FFFFFF", "#0284C7"
    )

    draw_node(
        3.5, 59.0, 21, 14.5,
        "Streamlit Dashboard (app.py)",
        "• app.py: Executive Dashboard & Sliders\n• Page 1: Academic Overview (Cohort KPIs)\n• Page 2: Analyze Student (Single Review)\n• Page 3: Agent Workflow (LangGraph Trace)\n• Page 4: Intervention Reports (18 Fields)\n• Page 5: Batch Analysis (Section Screening)\n• Page 6: Methodology, Ethics & Benchmarks",
        "FRONTEND", "#FFFFFF", "#0284C7"
    )

    draw_arrow((14.0, 75.5), (14.0, 73.5), label="Interacts", color="#0284C7", lw=2)

    # -------------------------------------------------------------------------
    # CONTAINER 2: LangGraph Orchestrator (Center Area)
    # -------------------------------------------------------------------------
    draw_container(28, 2, 40, 87, "LAYER 2: LANGGRAPH ORCHESTRATOR", "State Machine & Agents", "#EFF6FF", "#2563EB")

    # Shared State Box
    draw_node(
        30, 78.5, 36, 7.5,
        "Typed Shared State: EduPilotState",
        "request_id, student_id, execution_plan, indicators, concerns, evidence,\ninterventions, validation_results, retry_count, execution_trace, report",
        "TYPED DICT", "#DBEAFE", "#1D4ED8"
    )

    # Node 1: Input Validation
    draw_node(
        30, 68.0, 36, 7.5,
        "Node 1: Input Validation",
        "Validates regex pattern '^STU\\d{3,6}$' and checks existence in synthetic registry.\nRoutes to Planning Agent if valid; bypasses to Report Generator if invalid.",
        "GATEWAY", "#FFFFFF", "#2563EB"
    )

    # Node 2: Academic Planning Agent
    draw_node(
        30, 56.5, 36, 8.5,
        "Node 2: Academic Planning Agent",
        "Interprets objective, determines indicators to compute (attendance %, marks %,\ndecline delta, missing assignments), and formulates an ordered 6-step plan.",
        "GOAL-BASED AGENT", "#FFFFFF", "#2563EB"
    )

    # Node 3: Student Analytics Agent
    draw_node(
        30, 44.5, 36, 9.0,
        "Node 3: Student Analytics Agent",
        "Queries academic records via MCP client tools. Calculates subject indicators,\nevaluates threshold rules, flags concerns, and compiles traceable evidence.",
        "MODEL-BASED REFLEX", "#FFFFFF", "#0D9488"
    )

    # Node 4: Intervention Planning Agent
    draw_node(
        30, 32.5, 36, 9.0,
        "Node 4: Intervention Planning Agent",
        "Synthesizes tailored pedagogical support roadmaps with assigned academic\nroles, suggested review periods (1-4 weeks), and measurable follow-up goals.",
        "UTILITY-BASED AGENT", "#FFFFFF", "#D97706"
    )

    # Node 5: Critic & Validation Agent
    draw_node(
        30, 19.5, 36, 10.0,
        "Node 5: Critic & Validation Agent",
        "Adversarially recomputes calculations, asserts mathematical invariants\n(attended <= held, 0 <= marks <= max), audits thresholds, and verifies grounding.",
        "LEARNING & AUDIT", "#FFFFFF", "#7C3AED"
    )

    # Node 6: Correction Node
    draw_node(
        30, 5.5, 17, 10.5,
        "Node 6: Correction",
        "Increments retry counter (max 2),\nprunes ungrounded claims, and\nloops back to Analytics.",
        "CORRECTION LOOP", "#FEF3C7", "#D97706"
    )

    # Node 7: Report Generator Node
    draw_node(
        49, 5.5, 17, 10.5,
        "Node 7: Report Generator",
        "Assembles standardized 18-field\nacademic report with final status\n(VALIDATED / NEEDS_REVIEW).",
        "COMPLETION", "#DCFCE7", "#16A34A"
    )

    # -------------------------------------------------------------------------
    # LangGraph Flow Transitions
    # -------------------------------------------------------------------------
    # UI -> Node 1
    draw_arrow((24.5, 66.0), (30.0, 71.5), label="Execute Run", color="#0284C7", lw=2)

    # Node 1 -> State
    draw_arrow((48.0, 75.5), (48.0, 78.5), color="#1D4ED8", lw=1.5, ls=":")

    # Node 1 -> Node 2 (Valid)
    draw_arrow((48.0, 68.0), (48.0, 65.0), label="Valid Student", color="#2563EB", lw=2)

    # Node 2 -> Node 3
    draw_arrow((48.0, 56.5), (48.0, 53.5), label="Execution Plan", color="#2563EB", lw=2)

    # Node 3 -> Node 4
    draw_arrow((48.0, 44.5), (48.0, 41.5), label="Indicators & Evidence", color="#0D9488", lw=2)

    # Node 4 -> Node 5
    draw_arrow((48.0, 32.5), (48.0, 29.5), label="Proposed Interventions", color="#D97706", lw=2)

    # Node 5 -> Node 7 (Validation Passed)
    draw_arrow((57.5, 19.5), (57.5, 16.0), label="Pass: Validated", color="#16A34A", lw=2.5)

    # Node 5 -> Node 6 (Validation Discrepancy & Retry < 2)
    draw_arrow((38.5, 19.5), (38.5, 16.0), label="Discrepancy (Retry < 2)", color="#D97706", lw=2)

    # Node 6 loops back to Node 3 (Recalculate Loop) - Left perimeter
    draw_arrow((30.0, 11.0), (30.0, 49.0), label="Correction Loop", color="#D97706", lw=2, rad=-0.28, ls="--")

    # Node 6 -> Node 7 (Retry Exhausted)
    draw_arrow((47.0, 10.5), (49.0, 10.5), label="Exhausted", color="#DC2626", lw=1.5, ls=":")

    # Input Validation -> Node 7 (Bypass on Invalid Student ID) - Right perimeter
    draw_arrow((66.0, 71.5), (66.0, 11.0), label="Invalid ID Bypass", color="#DC2626", lw=2, rad=0.28, ls="--")

    # -------------------------------------------------------------------------
    # CONTAINER 3: Model Context Protocol (MCP 2.x) (Top Right)
    # -------------------------------------------------------------------------
    draw_container(70, 46, 28, 43, "LAYER 3: MODEL CONTEXT PROTOCOL", "Standardized Tool Abstraction", "#F0FDFA", "#0D9488")

    draw_node(
        71.5, 78.5, 25, 6.5,
        "EduPilot MCP Client",
        "Executes async/sync MCP tool calls, validates schemas,\nand records latency & status telemetry for UI observability.",
        "MCP CLIENT", "#FFFFFF", "#0D9488"
    )

    draw_node(
        71.5, 69.5, 25, 6.5,
        "Local Academic MCP Server",
        "Built on MCPServer (MCP 2.x SDK). Supports in-process\nor standalone stdio transport ('py -m mcp_server.server').",
        "MCP SERVER", "#FFFFFF", "#0D9488"
    )

    draw_arrow((84.0, 78.5), (84.0, 76.0), lw=1.5, color="#0D9488")

    # 7 Academic MCP Tools Card
    tools_card = FancyBboxPatch(
        (71.5, 48.0), 25, 19.5,
        boxstyle="round,pad=0.4,rounding_size=0.8",
        facecolor="#FFFFFF", edgecolor="#0D9488", linewidth=1.5
    )
    ax.add_patch(tools_card)
    ax.text(72.5, 65.5, "[TOOLS] Registered 7 Academic MCP Tools", fontsize=10.5, fontweight="bold", color="#0F766E")

    tools_list = [
        "1. get_student_profile(student_id)",
        "2. get_attendance_history(student_id)",
        "3. get_assessment_results(student_id)",
        "4. get_assignment_status(student_id)",
        "5. calculate_attendance(student_id)",
        "6. calculate_academic_indicators(student_id)",
        "7. validate_intervention_plan(plan, indicators)"
    ]
    for idx, t_name in enumerate(tools_list):
        ax.text(73.0, 62.8 - (idx * 2.05), t_name, fontsize=8.5, color="#134E4A", family="monospace")

    draw_arrow((84.0, 69.5), (84.0, 67.5), lw=1.5, color="#0D9488")

    # Analytics Agent <-> MCP Client connection
    draw_arrow((66.0, 47.0), (71.5, 81.5), label="MCP Tool Invocation", color="#0D9488", lw=2, rad=-0.18)

    # -------------------------------------------------------------------------
    # CONTAINER 4: Data & Deterministic Decision Engine (Bottom Right)
    # -------------------------------------------------------------------------
    draw_container(70, 2, 28, 42, "LAYER 4: DATA & DECISION ENGINE", "Deterministic & Reproducible", "#F0FDF4", "#16A34A")

    draw_node(
        71.5, 32.0, 25, 8.0,
        "Decision Rules Engine",
        "• Attendance < 75% -> ATTENDANCE_LOW\n• Marks < 40% -> ACADEMIC_PERFORMANCE_LOW\n• Score Drop >= 15% pts -> PERFORMANCE_DECLINE\n• Missing Assignments > 0 -> ASSIGNMENT_INCOMPLETE",
        "RULES ENGINE", "#FFFFFF", "#16A34A"
    )

    draw_node(
        71.5, 21.0, 25, 9.0,
        "Data Service & Invariants",
        "• Enforces attended <= classes_held\n• Enforces 0 <= marks <= maximum_marks\n• Handles division by zero safely\n• Detects DATA_INCOMPLETE explicitly",
        "DATA SERVICE", "#FFFFFF", "#16A34A"
    )

    draw_arrow((84.0, 32.0), (84.0, 30.0), lw=1.5, color="#16A34A")

    # Synthetic Datasets Card
    data_card = FancyBboxPatch(
        (71.5, 4.0), 25, 15.0,
        boxstyle="round,pad=0.4,rounding_size=0.8",
        facecolor="#FFFFFF", edgecolor="#16A34A", linewidth=1.5
    )
    ax.add_patch(data_card)
    ax.text(72.5, 17.0, "[DATASTORE] Synthetic Datasets (Seed = 42)", fontsize=10.5, fontweight="bold", color="#166534")

    datasets_list = [
        "• data/students.csv (100 student records)",
        "• data/attendance.csv (393 attendance logs)",
        "• data/assessments.csv (786 sequential scores)",
        "• data/assignments.csv (786 submissions)",
        "• data/scenarios_meta.json (Archetypes)"
    ]
    for idx, d_name in enumerate(datasets_list):
        ax.text(73.0, 14.8 - (idx * 2.05), d_name, fontsize=8.5, color="#14532D", family="monospace")

    draw_arrow((84.0, 21.0), (84.0, 19.0), lw=1.5, color="#16A34A")
    draw_arrow((84.0, 48.0), (84.0, 40.0), label="Queries & Evaluates", color="#16A34A", lw=1.5)

    # -------------------------------------------------------------------------
    # CONTAINER 5: Output Artifact: Academic Intervention Report (Bottom Left)
    # -------------------------------------------------------------------------
    draw_container(2, 2, 24, 53, "OUTPUT: INTERVENTION REPORT", "Standardized 18-Field Audit Record", "#FAF5FF", "#7C3AED")

    draw_node(
        3.5, 34.0, 21, 17.5,
        "18-Field Standardized Report",
        "• 1-5: Report ID, Timestamp, Student ID,\n  Term, and Analysis Objective\n• 6: Planning Agent's 6-Step Plan\n• 7-9: Attendance, Assessment, Assignment KPIs\n• 10-11: Flagged Concerns & Verifiable Evidence\n• 12-15: Interventions, Roles, Review Period,\n  and Expected Measurable Outcomes\n• 16: Missing Data & Systemic Limitations\n• 17: Critic Validation Results & Checks\n• 18: Final Audit Status",
        "STRUCTURED REPORT", "#FFFFFF", "#7C3AED"
    )

    draw_node(
        3.5, 19.0, 21, 13.5,
        "Audit Status Categorization",
        "• VALIDATED:\n  All calculations & invariants verified\n  by independent Critic Agent.\n\n• NEEDS_REVIEW:\n  Discrepancy persists beyond 2 retries;\n  flagged for faculty manual inspection.\n\n• VALIDATION_FAILED:\n  Invalid input ID or corrupt dataset.",
        "AUDIT STATUS", "#FFFFFF", "#7C3AED"
    )

    draw_node(
        3.5, 4.0, 21, 13.5,
        "Export & Persistence",
        "• One-Click JSON Download\n• Session CSV Summary Export\n• Batch Screening Priority Table\n• Persisted to data/reports/\n\n*Strict Decision Support Boundary:\nHuman faculty approval required.",
        "PERSISTENCE", "#FFFFFF", "#7C3AED"
    )

    # Route from Node 7 to Output Container along bottom
    draw_arrow((49.0, 10.5), (24.5, 10.5), label="Assemble Final Report", color="#7C3AED", lw=2)

    # Output delivered to UI
    draw_arrow((14.0, 51.5), (14.0, 59.0), label="Render in Dashboard", color="#0284C7", lw=2)

    # Save to file
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"[OK] Successfully generated refined high-resolution architecture diagram at {output_path}")


if __name__ == "__main__":
    generate_architecture_png()
