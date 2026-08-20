"""Deterministic Markdown & Knowledge Graph Parser."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class KnowledgeAsset:
    """Represents an atomic knowledge asset within the repository."""
    id: str
    filepath: Path
    title: str
    content: str
    frontmatter: Dict[str, str] = field(default_factory=dict)
    outgoing_links: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    word_count: int = 0
    mtime: float = 0.0
    is_moc: bool = False
    is_synthesis: bool = False


class KnowledgeGraph:
    """Attributed Directed Graph representation of the knowledge repository."""

    def __init__(self, name: str = "KnowledgeGraph"):
        self.name = name
        self.graph = nx.DiGraph()
        self.assets: Dict[str, KnowledgeAsset] = {}

    def add_asset(self, asset: KnowledgeAsset) -> None:
        """Add an asset node to the graph."""
        self.assets[asset.id] = asset
        self.graph.add_node(
            asset.id,
            title=asset.title,
            filepath=str(asset.filepath),
            word_count=asset.word_count,
            mtime=asset.mtime,
            is_moc=asset.is_moc,
            is_synthesis=asset.is_synthesis,
            tags=list(asset.tags),
        )

    def build_edges(self) -> None:
        """Resolve links and build directed edges."""
        for src_id, asset in self.assets.items():
            for target in asset.outgoing_links:
                # Target can match exact ID or title or basename
                target_id = self._resolve_target(target)
                if target_id:
                    self.graph.add_edge(src_id, target_id)
                else:
                    # Phantom / Broken link
                    self.graph.add_node(target, is_phantom=True)
                    self.graph.add_edge(src_id, target, broken=True)

    def _resolve_target(self, target: str) -> Optional[str]:
        target_norm = target.strip().lower()
        # Direct match
        if target in self.assets:
            return target
        # Case-insensitive / stem match
        for aid, asset in self.assets.items():
            if aid.lower() == target_norm:
                return aid
            if asset.title.lower() == target_norm:
                return aid
            if asset.filepath.stem.lower() == target_norm:
                return aid
        return None

    @property
    def node_count(self) -> int:
        return len(self.assets)

    @property
    def edge_count(self) -> int:
        return self.graph.number_of_edges()


class VaultParser:
    """Parser that scans a directory and extracts the knowledge graph."""

    # Regex for Wiki-links: [[Target|Alias]] or [[Target]]
    WIKI_LINK_PATTERN = re.compile(r"\[\[([^\|\]]+)(?:\|[^\]]+)?\]\]")
    # Regex for Markdown links: [Text](path/to/target.md)
    MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
    # Regex for Frontmatter
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    # Regex for Tags
    TAG_PATTERN = re.compile(r"(?:^|\s)#([a-zA-Z0-9_\-/]+)")

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def parse(self) -> KnowledgeGraph:
        """Scan and parse all markdown files in root_dir."""
        kg = KnowledgeGraph(name=self.root_dir.name)

        if not self.root_dir.exists():
            return kg

        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".md"):
                    filepath = Path(root) / file
                    asset = self._parse_file(filepath)
                    if asset:
                        kg.add_asset(asset)

        kg.build_edges()
        return kg

    def _parse_file(self, filepath: Path) -> Optional[KnowledgeAsset]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return None

        # Extract frontmatter
        fm_dict: Dict[str, str] = {}
        fm_match = self.FRONTMATTER_PATTERN.match(content)
        body = content
        if fm_match:
            fm_text = fm_match.group(1)
            body = content[fm_match.end():]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm_dict[k.strip()] = v.strip().strip('"\'')

        asset_id = fm_dict.get("id", filepath.stem)
        title = fm_dict.get("title", filepath.stem)

        # Extract outgoing links
        wiki_links = set(self.WIKI_LINK_PATTERN.findall(content))
        md_links = {Path(p).stem for _, p in self.MD_LINK_PATTERN.findall(content)}
        all_links = wiki_links.union(md_links)

        # Extract tags
        tags = set(self.TAG_PATTERN.findall(body))
        if "tags" in fm_dict:
            fm_tags = [t.strip() for t in fm_dict["tags"].strip("[]").split(",") if t.strip()]
            tags.update(fm_tags)

        # Word count & mtime
        word_count = len(body.split())
        mtime = filepath.stat().st_mtime if filepath.exists() else 0.0

        is_moc = "MOC" in filepath.name or "00_MOC" in filepath.name or "moc" in tags
        is_synthesis = "synthesis" in tags or "paper" in tags or "thesis" in tags

        return KnowledgeAsset(
            id=asset_id,
            filepath=filepath,
            title=title,
            content=content,
            frontmatter=fm_dict,
            outgoing_links=all_links,
            tags=tags,
            word_count=word_count,
            mtime=mtime,
            is_moc=is_moc,
            is_synthesis=is_synthesis,
        )
