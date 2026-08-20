"""Unit tests for VaultParser and KnowledgeGraph."""

import tempfile
from pathlib import Path
import pytest

from cognitive_metabolism.parser import VaultParser, KnowledgeAsset, KnowledgeGraph


def test_parser_basic(tmp_path: Path):
    # Create sample files
    f1 = tmp_path / "NoteA.md"
    f1.write_text(
        "---\nid: NoteA\ntitle: Note A\ntags: [concept]\n---\n# Note A\nLinks to [[NoteB|Alias B]] and [[NoteC]].",
        encoding="utf-8"
    )

    f2 = tmp_path / "NoteB.md"
    f2.write_text(
        "---\nid: NoteB\ntitle: Note B\n---\n# Note B\nLinks back to [[NoteA]].",
        encoding="utf-8"
    )

    f3 = tmp_path / "NoteC.md"
    f3.write_text(
        "# Note C\nLinks to non-existent [[NoteD]].",
        encoding="utf-8"
    )

    parser = VaultParser(tmp_path)
    kg = parser.parse()

    assert kg.node_count == 3
    assert "NoteA" in kg.assets
    assert "NoteB" in kg.assets
    assert "NoteC" in kg.assets

    # Check edges
    assert kg.graph.has_edge("NoteA", "NoteB")
    assert kg.graph.has_edge("NoteA", "NoteC")
    assert kg.graph.has_edge("NoteB", "NoteA")
    assert kg.graph.has_edge("NoteC", "NoteD")
    assert kg.graph.edges["NoteC", "NoteD"].get("broken", False) is True


def test_parser_empty_dir(tmp_path: Path):
    parser = VaultParser(tmp_path)
    kg = parser.parse()
    assert kg.node_count == 0
    assert kg.edge_count == 0
