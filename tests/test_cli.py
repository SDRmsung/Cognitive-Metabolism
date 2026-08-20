"""Unit tests for cm-audit CLI."""

import json
from pathlib import Path
import pytest

from cognitive_metabolism.cli import main


def test_cli_scan(tmp_path: Path, capsys):
    f1 = tmp_path / "NoteA.md"
    f1.write_text("# Note A\nContent here.", encoding="utf-8")

    exit_code = main(["scan", str(tmp_path)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "COGNITIVE METABOLISM: KNOWLEDGE HEALTH REPORT" in captured.out


def test_cli_scan_json(tmp_path: Path, capsys):
    f1 = tmp_path / "NoteA.md"
    f1.write_text("# Note A\nContent here.", encoding="utf-8")

    exit_code = main(["scan", str(tmp_path), "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_assets"] == 1
    assert "knowledge_health_index" in data
