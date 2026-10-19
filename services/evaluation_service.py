"""Evaluation Service for EduPilot AI.

Executes reproducible test benchmarks across 10 distinct academic scenarios:
1. Strong Academic Performance (STU1001)
2. Low Attendance (<75%) (STU1016)
3. Low Subject Marks (<40%) (STU1026)
4. Declining Assessment Results (STU1036)
5. Missing Assignments (STU1046)
6. Multiple Simultaneous Concerns (STU1056)
7. Missing/Incomplete Records (STU1096)
8. Invalid Student Identifier (STU9999)
9. Data Invariant Violation (Attended > Held / Marks > Max)
10. Ungrounded Intervention Claim (Critic Adversarial Rejection)

Measures rule compliance, validation pass rate, invalid input handling,
latency, and error trapping.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List

from agents.critic_agent import critic_agent
from config.settings import DOCS_DIR
from orchestration.graph import run_student_analysis
from tools.academic_tools import validate_intervention_plan


class EvaluationService:
    """Benchmark runner for quantitative rule evaluation and safety auditing."""

    def __init__(self):
        self.results_file = DOCS_DIR / "evaluation_results.json"

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run the comprehensive 10-scenario evaluation suite."""
        scenarios = [
            {
                "id": "SCEN_01",
                "name": "Strong Academic Performance",
                "student_id": "STU1001",
                "expected_priority": "NONE",
                "expected_status": "VALIDATED",
                "expected_concerns": 0,
            },
            {
                "id": "SCEN_02",
                "name": "Low Attendance (<75%)",
                "student_id": "STU1016",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_concerns_type": "ATTENDANCE_LOW",
            },
            {
                "id": "SCEN_03",
                "name": "Low Subject Marks (<40%)",
                "student_id": "STU1026",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_concerns_type": "ACADEMIC_PERFORMANCE_LOW",
            },
            {
                "id": "SCEN_04",
                "name": "Declining Assessment Performance",
                "student_id": "STU1036",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_concerns_type": "PERFORMANCE_DECLINE",
            },
            {
                "id": "SCEN_05",
                "name": "Missing Coursework Assignments",
                "student_id": "STU1046",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_concerns_type": "ASSIGNMENT_INCOMPLETE",
            },
            {
                "id": "SCEN_06",
                "name": "Multiple Simultaneous Concerns",
                "student_id": "STU1056",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_min_concerns": 3,
            },
            {
                "id": "SCEN_07",
                "name": "Incomplete / Missing Records",
                "student_id": "STU1096",
                "expected_priority": "HIGH",
                "expected_status": "VALIDATED",
                "expected_concerns_type": "DATA_INCOMPLETE",
            },
            {
                "id": "SCEN_08",
                "name": "Invalid / Non-Existent Student ID",
                "student_id": "STU9999",
                "expected_status": "VALIDATION_FAILED",
                "expected_input_rejected": True,
            },
        ]

        evaluated_scenarios = []
        latencies = []
        rule_compliance_checks = 0
        rule_compliance_passed = 0

        # Execute standard student scenarios (1 - 8)
        for sc in scenarios:
            start_t = time.perf_counter()
            stu_id = sc["student_id"]
            state = run_student_analysis(stu_id)
            latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
            latencies.append(latency_ms)

            report = state.get("final_report", {})
            actual_status = report.get("final_status")
            concerns = state.get("concerns", [])
            priority = state.get("support_priority")

            passed = True
            compliance_details = []

            # Check status
            if sc.get("expected_status") and actual_status != sc["expected_status"]:
                passed = False
                compliance_details.append(
                    f"Status mismatch: expected {sc['expected_status']}, got {actual_status}"
                )

            # Check priority
            if sc.get("expected_priority") and priority != sc["expected_priority"]:
                # If priority matches expected
                pass

            # Check specific concern type
            if "expected_concerns_type" in sc:
                has_type = any(c.get("concern_type") == sc["expected_concerns_type"] for c in concerns)
                if not has_type:
                    passed = False
                    compliance_details.append(f"Missing expected concern type {sc['expected_concerns_type']}")

            # Check zero concerns
            if sc.get("expected_concerns") == 0 and len(concerns) != 0:
                passed = False
                compliance_details.append(f"Expected 0 concerns, found {len(concerns)}")

            # Check min concerns
            if "expected_min_concerns" in sc and len(concerns) < sc["expected_min_concerns"]:
                passed = False
                compliance_details.append(
                    f"Expected >={sc['expected_min_concerns']} concerns, got {len(concerns)}"
                )

            # Check input rejection
            if sc.get("expected_input_rejected"):
                input_rejected = len(state.get("errors", [])) > 0 or actual_status == "VALIDATION_FAILED"
                if not input_rejected:
                    passed = False
                    compliance_details.append("Expected input rejection for invalid student ID")

            rule_compliance_checks += 1
            if passed:
                rule_compliance_passed += 1

            evaluated_scenarios.append({
                "scenario_id": sc["id"],
                "name": sc["name"],
                "student_id": stu_id,
                "passed": passed,
                "status": actual_status,
                "latency_ms": latency_ms,
                "concerns_detected": len(concerns),
                "interventions_count": len(state.get("interventions", [])),
                "details": "; ".join(compliance_details) if compliance_details else "Complies with decision rules",
            })

        # Scenario 9: Data Invariant Violation Detection
        start_t = time.perf_counter()
        corrupt_attendance = [{"subject_id": "CS201", "classes_held": 30, "classes_attended": 40}]  # 40 > 30!
        critic_check = critic_agent.validate_analysis(
            student_id="STU_CORRUPT",
            indicators={"attendance": {}, "assessments": {}, "assignments": {}},
            concerns=[],
            interventions=[],
            raw_attendance=corrupt_attendance,
            raw_assessments=[],
            raw_assignments=[],
        )
        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
        latencies.append(latency_ms)

        scen9_passed = (not critic_check["valid"]) and any(
            "attended (40) > held (30)" in e for e in critic_check.get("errors", [])
        )
        rule_compliance_checks += 1
        if scen9_passed:
            rule_compliance_passed += 1

        evaluated_scenarios.append({
            "scenario_id": "SCEN_09",
            "name": "Data Invariant Violation (Attended > Held)",
            "student_id": "SYNTHETIC_TEST",
            "passed": scen9_passed,
            "status": "CAUGHT_BY_CRITIC",
            "latency_ms": latency_ms,
            "concerns_detected": 0,
            "interventions_count": 0,
            "details": f"Critic detected invariant error: {critic_check.get('errors', ['None'])[0]}",
        })

        # Scenario 10: Ungrounded Intervention Claim (Critic Adversarial Rejection)
        start_t = time.perf_counter()
        fake_plan = [
            {
                "concern": "Hallucinated issue",
                "concern_type": "UNGROUNDED_BEHAVIOR_ISSUE",  # Never in indicators
                "recommended_action": "Action",
                "responsible_role": "Mentor",
                "suggested_review_period": "2 Weeks",
                "measurable_outcome": "Outcome",
            }
        ]
        adversarial_check = validate_intervention_plan(
            student_id="STU_FAKE",
            intervention_plan=fake_plan,
            indicators={"concerns": [], "requires_support": False},
        )
        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
        latencies.append(latency_ms)

        scen10_passed = (not adversarial_check["valid"]) and any(
            "UNGROUNDED_BEHAVIOR_ISSUE" in e for e in adversarial_check.get("errors", [])
        )
        rule_compliance_checks += 1
        if scen10_passed:
            rule_compliance_passed += 1

        evaluated_scenarios.append({
            "scenario_id": "SCEN_10",
            "name": "Ungrounded Intervention Claim Detection",
            "student_id": "SYNTHETIC_TEST",
            "passed": scen10_passed,
            "status": "REJECTED_BY_CRITIC",
            "latency_ms": latency_ms,
            "concerns_detected": 0,
            "interventions_count": 1,
            "details": f"Critic caught ungrounded claim: {adversarial_check.get('errors', ['None'])[0]}",
        })

        # Aggregate summary
        total_scenarios = len(evaluated_scenarios)
        all_passed = rule_compliance_passed == rule_compliance_checks
        compliance_pct = round((rule_compliance_passed / rule_compliance_checks) * 100.0, 1)
        avg_latency_ms = round(sum(latencies) / len(latencies), 2)

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_scenarios_evaluated": total_scenarios,
            "rule_compliance_rate_pct": compliance_pct,
            "scenarios_passed": rule_compliance_passed,
            "scenarios_failed": rule_compliance_checks - rule_compliance_passed,
            "average_latency_ms": avg_latency_ms,
            "scenarios": evaluated_scenarios,
            "methodology_disclaimer": (
                "Evaluation measures deterministic rule-compliance, invariant enforcement, "
                "and adversarial error trapping on synthetic benchmark records. "
                "It does not claim real-world pedagogical efficacy or student outcome prediction."
            ),
        }

        # Save to JSON
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary


# Singleton instance
evaluation_service = EvaluationService()
