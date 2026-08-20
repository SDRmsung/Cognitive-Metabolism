"""Cognitive Metabolism: A Dynamic Epistemological & Graph-Theoretic Engine.

Core exports:
- VaultParser: Deterministic AST & Markdown graph parser
- DKHPCalculator: Dynamic Knowledge Health Profile 4D calculator
- SubtractivePruner: Pruning & active unlearning operator (O_exec)
- AuditEngine: Unified vault scanner and reporting engine
"""

from .parser import VaultParser, KnowledgeAsset, KnowledgeGraph
from .metrics.dkhp import DKHPCalculator, DKHPResult
from .pruning.engine import SubtractivePruner, PruningPlan
from .cli import AuditEngine

__version__ = "0.1.0"
__all__ = [
    "VaultParser",
    "KnowledgeAsset",
    "KnowledgeGraph",
    "DKHPCalculator",
    "DKHPResult",
    "SubtractivePruner",
    "PruningPlan",
    "AuditEngine",
]
