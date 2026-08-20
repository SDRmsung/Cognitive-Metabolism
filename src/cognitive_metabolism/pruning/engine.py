"""Subtractive Pruning & Active Unlearning Engine (O_exec Operator)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple

from ..metrics.dkhp import DKHPCalculator, DKHPResult
from ..parser import KnowledgeAsset, KnowledgeGraph


class ActionType(str, Enum):
    ARCHIVE_ORPHAN = "archive_orphan"
    FIX_BROKEN_LINK = "fix_broken_link"
    MERGE_DUPLICATE = "merge_duplicate"
    REFRESH_STALE = "refresh_stale"
    LINK_TO_MOC = "link_to_moc"


@dataclass
class PruningAction:
    action_type: ActionType
    target_id: str
    target_path: Path
    reason: str
    suggested_action: str
    confidence: float = 1.0


@dataclass
class PruningPlan:
    current_health: DKHPResult
    projected_health: DKHPResult
    actions: List[PruningAction] = field(default_factory=list)

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for a in self.actions:
            counts[a.action_type.value] = counts.get(a.action_type.value, 0) + 1
        return counts


class SubtractivePruner:
    """Calculates active subtraction and unlearning recommendations."""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.g = kg.graph
        self.assets = kg.assets

    def generate_plan(self, current_time: float | None = None) -> PruningPlan:
        now = current_time if current_time is not None else time.time()
        calc = DKHPCalculator(self.kg)
        current_res = calc.compute(now)

        actions: List[PruningAction] = []

        # 1. Detect Orphans
        for aid, asset in self.assets.items():
            if aid in self.g:
                in_deg = self.g.in_degree(aid)
                out_deg = self.g.out_degree(aid)
                if in_deg == 0 and out_deg == 0:
                    # Check if small scratch note or stale
                    dt_days = (now - asset.mtime) / 86400.0 if asset.mtime > 0 else 0
                    if asset.word_count < 50 and dt_days > 30:
                        actions.append(
                            PruningAction(
                                action_type=ActionType.ARCHIVE_ORPHAN,
                                target_id=aid,
                                target_path=asset.filepath,
                                reason=f"Orphan note with low content ({asset.word_count} words) and inactivity ({int(dt_days)} days).",
                                suggested_action=f"Move {asset.filepath.name} to archive/ or delete.",
                                confidence=0.90,
                            )
                        )
                    else:
                        actions.append(
                            PruningAction(
                                action_type=ActionType.LINK_TO_MOC,
                                target_id=aid,
                                target_path=asset.filepath,
                                reason=f"Substantive orphan note ({asset.word_count} words) lacks parent MOC reference.",
                                suggested_action=f"Add wiki-link from corresponding Area MOC to [[{aid}]].",
                                confidence=0.85,
                            )
                        )

        # 2. Detect Broken Links
        for aid, asset in self.assets.items():
            if aid in self.g:
                for _, target, data in self.g.out_edges(aid, data=True):
                    if data.get("broken", False):
                        actions.append(
                            PruningAction(
                                action_type=ActionType.FIX_BROKEN_LINK,
                                target_id=aid,
                                target_path=asset.filepath,
                                reason=f"Outgoing link to non-existent target '[[{target}]]'.",
                                suggested_action=f"Create target note [[{target}]] or remove broken link from {asset.filepath.name}.",
                                confidence=1.0,
                            )
                        )

        # 3. Detect Near-Duplicate Titles
        titles: Dict[str, str] = {}
        for aid, asset in self.assets.items():
            norm_title = asset.title.strip().lower()
            if norm_title in titles:
                orig_id = titles[norm_title]
                actions.append(
                    PruningAction(
                        action_type=ActionType.MERGE_DUPLICATE,
                        target_id=aid,
                        target_path=asset.filepath,
                        reason=f"Duplicate title '{asset.title}' matches existing note '{orig_id}'.",
                        suggested_action=f"Consolidate {aid} into {orig_id} and redirect links.",
                        confidence=0.95,
                    )
                )
            else:
                titles[norm_title] = aid

        # Estimate Projected Health (assuming orphan rate drops and broken links fixed)
        projected_orphans = max(0, current_res.orphan_count - len([a for a in actions if a.action_type in (ActionType.ARCHIVE_ORPHAN, ActionType.LINK_TO_MOC)]))
        n = max(1, current_res.total_assets)
        proj_orphan_rate = projected_orphans / n
        proj_coverage = min(1.0, current_res.dependency_coverage + 0.15)
        proj_validity = min(1.0, current_res.validity_score + 0.15)
        proj_norm_entropy = 0.55  # Converges to optimal
        proj_entropy_fit = 1.0

        proj_health = 100.0 * (
            (1.0 - proj_orphan_rate) * 0.30 +
            proj_entropy_fit * 0.25 +
            proj_coverage * 0.25 +
            proj_validity * 0.20
        )

        projected_res = DKHPResult(
            total_assets=current_res.total_assets,
            total_edges=current_res.total_edges + len([a for a in actions if a.action_type == ActionType.LINK_TO_MOC]),
            orphan_count=projected_orphans,
            orphan_rate=proj_orphan_rate,
            structural_entropy=current_res.structural_entropy,
            normalized_entropy=proj_norm_entropy,
            dependency_coverage=proj_coverage,
            validity_score=proj_validity,
            broken_link_count=0,
            knowledge_health_index=min(100.0, proj_health),
        )

        return PruningPlan(
            current_health=current_res,
            projected_health=projected_res,
            actions=actions,
        )
