"""Dynamic Knowledge Health Profile (DKHP) Computable 4D Vector."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import networkx as nx
import numpy as np

from ..parser import KnowledgeGraph


@dataclass
class DKHPResult:
    """Computable 4D DKHP metric profile and overall health index."""
    total_assets: int
    total_edges: int
    orphan_count: int
    orphan_rate: float            # rho_orphan in [0, 1]
    structural_entropy: float      # H(G)
    normalized_entropy: float      # H_norm in [0, 1]
    dependency_coverage: float     # C_dep in [0, 1]
    validity_score: float          # U in [0, 1]
    broken_link_count: int
    knowledge_health_index: float  # Composite 0 - 100

    def to_dict(self) -> Dict[str, float | int]:
        return {
            "total_assets": self.total_assets,
            "total_edges": self.total_edges,
            "orphan_count": self.orphan_count,
            "orphan_rate": round(self.orphan_rate, 4),
            "structural_entropy": round(self.structural_entropy, 4),
            "normalized_entropy": round(self.normalized_entropy, 4),
            "dependency_coverage": round(self.dependency_coverage, 4),
            "validity_score": round(self.validity_score, 4),
            "broken_link_count": self.broken_link_count,
            "knowledge_health_index": round(self.knowledge_health_index, 2),
        }


class DKHPCalculator:
    """Calculates the 4D Dynamic Knowledge Health Profile from a KnowledgeGraph."""

    # Target homeostatic entropy band centroid
    OPTIMAL_ENTROPY_RATIO = 0.55
    # Half-life for temporal freshness decay in days
    DECAY_HALF_LIFE_DAYS = 180.0

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.g = kg.graph
        self.assets = kg.assets

    def compute(self, current_time: float | None = None) -> DKHPResult:
        n = len(self.assets)
        if n == 0:
            return DKHPResult(
                total_assets=0,
                total_edges=0,
                orphan_count=0,
                orphan_rate=0.0,
                structural_entropy=0.0,
                normalized_entropy=0.0,
                dependency_coverage=0.0,
                validity_score=0.0,
                broken_link_count=0,
                knowledge_health_index=0.0,
            )

        now = current_time if current_time is not None else time.time()

        # 1. Orphan Rate
        orphans = 0
        for aid in self.assets:
            if aid in self.g:
                in_deg = self.g.in_degree(aid)
                out_deg = self.g.out_degree(aid)
                if in_deg == 0 and out_deg == 0:
                    orphans += 1
            else:
                orphans += 1
        orphan_rate = orphans / n

        # 2. Structural Entropy (Shannon degree distribution entropy)
        degrees = [self.g.degree(aid) for aid in self.assets if aid in self.g]
        total_deg = sum(degrees)
        if total_deg > 0:
            probs = [d / total_deg for d in degrees if d > 0]
            entropy = -sum(p * math.log2(p) for p in probs)
            max_entropy = math.log2(n) if n > 1 else 1.0
            norm_entropy = min(1.0, entropy / max_entropy) if max_entropy > 0 else 0.0
        else:
            entropy = 0.0
            norm_entropy = 0.0

        # 3. Dependency Coverage (Directed Reachability to MOC / Synthesis hubs)
        moc_nodes = [aid for aid, a in self.assets.items() if a.is_moc or a.is_synthesis]
        if not moc_nodes:
            # Fallback: Top 10% highest in-degree nodes as hubs
            sorted_nodes = sorted(
                self.assets.keys(),
                key=lambda x: self.g.in_degree(x) if x in self.g else 0,
                reverse=True
            )
            moc_nodes = sorted_nodes[:max(1, int(n * 0.1))]

        # Find all nodes connected (in or out) to at least one hub or part of a component >= 3
        connected_to_hubs: Set[str] = set(moc_nodes)
        for hub in moc_nodes:
            if hub in self.g:
                # Predecessors and successors
                connected_to_hubs.update(nx.ancestors(self.g, hub))
                connected_to_hubs.update(nx.descendants(self.g, hub))

        dep_coverage = len(connected_to_hubs.intersection(self.assets.keys())) / n

        # 4. Validity & Broken Links
        broken_links = 0
        validity_sum = 0.0
        decay_lambda = math.log(2) / (self.DECAY_HALF_LIFE_DAYS * 86400.0)

        for aid, asset in self.assets.items():
            # Check broken links
            file_broken = 0
            if aid in self.g:
                for _, target, data in self.g.out_edges(aid, data=True):
                    if data.get("broken", False):
                        file_broken += 1
            broken_links += file_broken

            out_count = max(1, len(asset.outgoing_links))
            broken_penalty = max(0.0, 1.0 - (file_broken / out_count))

            # Temporal decay (freshness)
            dt = max(0.0, now - asset.mtime) if asset.mtime > 0 else 0.0
            freshness = math.exp(-decay_lambda * dt)

            asset_validity = (broken_penalty * 0.7) + (freshness * 0.3)
            validity_sum += asset_validity

        validity_score = validity_sum / n

        # Composite Index (0 - 100)
        # Penalize orphan rate, entropy deviation from optimal band, reward coverage and validity
        entropy_fit = max(0.0, 1.0 - abs(norm_entropy - self.OPTIMAL_ENTROPY_RATIO) * 2.0)
        health_index = 100.0 * (
            (1.0 - orphan_rate) * 0.30 +
            entropy_fit * 0.25 +
            dep_coverage * 0.25 +
            validity_score * 0.20
        )
        health_index = max(0.0, min(100.0, health_index))

        return DKHPResult(
            total_assets=n,
            total_edges=self.kg.edge_count,
            orphan_count=orphans,
            orphan_rate=orphan_rate,
            structural_entropy=entropy,
            normalized_entropy=norm_entropy,
            dependency_coverage=dep_coverage,
            validity_score=validity_score,
            broken_link_count=broken_links,
            knowledge_health_index=health_index,
        )
