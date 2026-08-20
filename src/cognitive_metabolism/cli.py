"""CLI Interface for Cognitive Metabolism Audit Engine (cm-audit)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from tabulate import tabulate

from .metrics.dkhp import DKHPCalculator, DKHPResult
from .parser import VaultParser
from .pruning.engine import SubtractivePruner


class AuditEngine:
    """High-level facade for auditing knowledge repositories."""

    @staticmethod
    def audit_path(vault_path: str | Path) -> tuple[DKHPResult, SubtractivePruner]:
        parser = VaultParser(vault_path)
        kg = parser.parse()
        calc = DKHPCalculator(kg)
        dkhp = calc.compute()
        pruner = SubtractivePruner(kg)
        return dkhp, pruner


def get_health_grade(score: float) -> str:
    if score >= 90.0:
        return "A+ (Optimal Homeostasis)"
    elif score >= 80.0:
        return "A  (Healthy)"
    elif score >= 70.0:
        return "B  (Mild Degradation)"
    elif score >= 55.0:
        return "C  (Severe Bloat / Entropy)"
    else:
        return "D  (Calcified Knowledge Silo)"


def scan_command(args: argparse.Namespace) -> int:
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"[Error] Target path '{target_path}' does not exist.", file=sys.stderr)
        return 1

    if not args.json:
        print(f"[*] Scanning Knowledge Vault: {target_path}")
    dkhp, pruner = AuditEngine.audit_path(target_path)

    if args.json:
        data = dkhp.to_dict()
        data["grade"] = get_health_grade(dkhp.knowledge_health_index)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"[+] Audit JSON exported to {args.output}")
        else:
            print(json.dumps(data, indent=2))
        return 0

    table_data = [
        ["Total Knowledge Assets (|V|)", str(dkhp.total_assets)],
        ["Total Relational Edges (|E|)", str(dkhp.total_edges)],
        ["Orphan Nodes Count", f"{dkhp.orphan_count} ({dkhp.orphan_rate*100:.1f}%)"],
        ["Structural Graph Entropy H(G)", f"{dkhp.structural_entropy:.4f} (Norm: {dkhp.normalized_entropy:.2f})"],
        ["Relational Dependency Coverage", f"{dkhp.dependency_coverage*100:.1f}%"],
        ["Actionable Validity Score (U)", f"{dkhp.validity_score:.4f}"],
        ["Broken / Phantom Links", str(dkhp.broken_link_count)],
        ["----------------------------", "--------------------"],
        ["Knowledge Health Index (0-100)", f"{dkhp.knowledge_health_index:.2f} / 100.0"],
        ["Diagnostic Health Grade", get_health_grade(dkhp.knowledge_health_index)],
    ]

    print("\n" + "=" * 55)
    print("  [CM] COGNITIVE METABOLISM: KNOWLEDGE HEALTH REPORT")
    print("=" * 55)
    print(tabulate(table_data, headers=["Metric Dimension", "Value"], tablefmt="rounded_grid"))
    print("\n")

    if args.plan:
        plan = pruner.generate_plan()
        print("[*] METABOLIC PRUNING & RECOVERY PLAN (O_exec):")
        print(f"  Total Recommended Interventions: {plan.total_actions}")
        print(f"  Projected Health Index: {plan.projected_health.knowledge_health_index:.2f} (+{plan.projected_health.knowledge_health_index - dkhp.knowledge_health_index:.2f})")
        print(f"  Summary: {plan.summary()}\n")

        if plan.actions[:10]:
            action_rows = [
                [a.action_type.value, a.target_id, a.reason[:40] + "...", a.suggested_action[:45] + "..."]
                for a in plan.actions[:10]
            ]
            print(tabulate(action_rows, headers=["Action Type", "Target", "Diagnostic Reason", "Remediation"], tablefmt="github"))
            if len(plan.actions) > 10:
                print(f"  ... and {len(plan.actions) - 10} more actions.")

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="cm-audit",
        description="Cognitive Metabolism Engine: Enterprise Knowledge Health & Agentic Memory Auditor",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a knowledge vault or repository")
    scan_parser.add_argument("path", nargs="?", default=".", help="Path to knowledge directory")
    scan_parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    scan_parser.add_argument("--plan", action="store_true", help="Include active pruning and remediation plan")
    scan_parser.add_argument("-o", "--output", help="Save output to file")

    args = parser.parse_args(argv)
    if not args.command or args.command == "scan":
        if not hasattr(args, "path"):
            args.path = "."
            args.json = False
            args.plan = False
            args.output = None
        return scan_command(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
