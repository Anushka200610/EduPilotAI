"""Evaluation Runner for EduPilot AI.

Executes reproducible academic scenarios, verifies threshold compliance,
critic validation, adversarial error trapping, and saves quantitative results.

Usage:
    py scripts/evaluate.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.evaluation_service import evaluation_service


def main():
    print("=" * 72)
    print(" EDUPILOT AI — ACADEMIC INTERVENTION BENCHMARK EVALUATION")
    print("=" * 72)
    print("Running 10 reproducible scenarios...\n")

    summary = evaluation_service.run_all_benchmarks()

    print(f"{'ID':<9} {'Scenario Name':<34} {'Status':<16} {'Time':<8} {'Passed'}")
    print("-" * 72)

    for sc in summary["scenarios"]:
        passed_mark = "[PASS]" if sc["passed"] else "[FAIL]"
        print(
            f"{sc['scenario_id']:<9} {sc['name']:<34} {sc['status']:<16} {sc['latency_ms']:>6.1f}ms  {passed_mark}"
        )

    print("-" * 72)
    print(f"Total Scenarios Evaluated : {summary['total_scenarios_evaluated']}")
    print(f"Rule Compliance Rate      : {summary['rule_compliance_rate_pct']}%")
    print(f"Passed Checks             : {summary['scenarios_passed']}/{summary['total_scenarios_evaluated']}")
    print(f"Average Execution Latency : {summary['average_latency_ms']} ms")
    print(f"Results Saved To          : {evaluation_service.results_file}")
    print("=" * 72)
    print("\n[NOTE] " + summary["methodology_disclaimer"] + "\n")


if __name__ == "__main__":
    main()
