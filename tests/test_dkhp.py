"""Unit tests for DKHPCalculator."""

from pathlib import Path
import pytest

from cognitive_metabolism.parser import VaultParser
from cognitive_metabolism.metrics.dkhp import DKHPCalculator


def test_dkhp_metrics(tmp_path: Path):
    # Setup a small vault: 1 MOC hub, 2 connected nodes, 1 isolated orphan
    f_moc = tmp_path / "00_MOC.md"
    f_moc.write_text(
        "---\nid: 00_MOC\ntitle: Master MOC\ntags: [moc]\n---\n# MOC\n- [[Node1]]\n- [[Node2]]",
        encoding="utf-8"
    )

    f1 = tmp_path / "Node1.md"
    f1.write_text("# Node 1\nLinks to [[00_MOC]] and [[Node2]].", encoding="utf-8")

    f2 = tmp_path / "Node2.md"
    f2.write_text("# Node 2\nLinks to [[00_MOC]].", encoding="utf-8")

    f3 = tmp_path / "Orphan.md"
    f3.write_text("# Orphan Note\nNo links here.", encoding="utf-8")

    parser = VaultParser(tmp_path)
    kg = parser.parse()
    calc = DKHPCalculator(kg)
    res = calc.compute()

    assert res.total_assets == 4
    assert res.orphan_count == 1
    assert res.orphan_rate == 0.25
    assert res.dependency_coverage >= 0.75
    assert res.structural_entropy > 0.0
    assert 0.0 <= res.knowledge_health_index <= 100.0


def test_dkhp_empty_graph(tmp_path: Path):
    parser = VaultParser(tmp_path)
    kg = parser.parse()
    calc = DKHPCalculator(kg)
    res = calc.compute()

    assert res.total_assets == 0
    assert res.knowledge_health_index == 0.0
