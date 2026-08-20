"""Unit tests for SubtractivePruner."""

from pathlib import Path
import pytest

from cognitive_metabolism.parser import VaultParser
from cognitive_metabolism.pruning.engine import SubtractivePruner, ActionType


def test_pruner_detects_broken_and_orphan(tmp_path: Path):
    f1 = tmp_path / "NoteA.md"
    f1.write_text("# Note A\nPoints to [[BrokenTarget]].", encoding="utf-8")

    f2 = tmp_path / "OrphanSmall.md"
    f2.write_text("# Tiny\norphan", encoding="utf-8")

    parser = VaultParser(tmp_path)
    kg = parser.parse()
    pruner = SubtractivePruner(kg)
    plan = pruner.generate_plan()

    assert plan.total_actions >= 2
    action_types = [a.action_type for a in plan.actions]
    assert ActionType.FIX_BROKEN_LINK in action_types
    assert (ActionType.ARCHIVE_ORPHAN in action_types or ActionType.LINK_TO_MOC in action_types)
    assert plan.projected_health.knowledge_health_index >= plan.current_health.knowledge_health_index
