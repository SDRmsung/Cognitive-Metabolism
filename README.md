<div align="center">

# 🧠 Cognitive Metabolism (`cm-audit`)

**A Dynamic Epistemological & Graph-Theoretic Engine for Enterprise Knowledge Health, Structural Entropy Reduction, and Agentic Memory Governance**

[![PyPI Version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](pyproject.toml)
[![CI Status](https://img.shields.io/badge/CI-Passing-brightgreen.svg)](.github/workflows/ci.yml)
[![Open Science](https://img.shields.io/badge/Open%20Science-Reproducible%20Benchmark-orange.svg)](benchmarks/)

</div>

---

## 📖 Overview

As enterprise knowledge bases, RAG pipelines, and autonomous AI agents expand, they inevitably suffer from the **Knowledge Accumulation Paradox**: *unmonitored asset accumulation degrades retrieval fidelity, expands candidate search spaces, and elevates decision latency*.

**Cognitive Metabolism** provides the mathematical foundations and open-source tooling (`cm-audit`) to model explicit knowledge repositories as **non-equilibrium living graphs** requiring continuous homeostatic regulation and active subtractive unlearning ($O_{\text{exec}}$).

```
   [ Enterprise Repositories / PKM Vaults ]
                      │
                      ▼
   ┌─────────────────────────────────────────┐
   │        VaultParser & AST Extractor      │
   │  - Wiki-links, Markdown DAGs, Metadata  │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────┐
   │     4D Dynamic Knowledge Health (DKHP)  │
   │  • Orphan Rate (ρ_orphan)               │
   │  • Structural Graph Entropy (H)         │
   │  • Relational Dependency Coverage (C)   │
   │  • Temporal Freshness & Validity (U)    │
   └──────────────────┬──────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────┐
   │    Subtractive Pruning Engine (O_exec)  │
   │  - Dead link remediation & healing      │
   │  - Orphan reconnection & unlearning     │
   │  - Redundancy de-bloat & clustering     │
   └─────────────────────────────────────────┘
```

---

## ⚡ Quickstart

### 1. Installation

```bash
git clone https://github.com/SDRmsung/Cognitive-Metabolism.git
cd Cognitive-Metabolism
pip install -e .
```

### 2. Audit a Knowledge Repository (CLI)

```bash
# Scan a markdown vault and print a health diagnostic report
cm-audit scan ./path/to/my_vault

# Export audit metrics to JSON
cm-audit scan ./path/to/my_vault --json -o health_report.json

# Generate an active pruning and unlearning remediation plan
cm-audit scan ./path/to/my_vault --plan
```

### 3. Python API Usage

```python
from cognitive_metabolism import VaultParser, DKHPCalculator, SubtractivePruner

# 1. Parse knowledge graph
parser = VaultParser("./my_knowledge_vault")
kg = parser.parse()

# 2. Compute 4D DKHP metrics
calc = DKHPCalculator(kg)
dkhp = calc.compute()
print(f"Health Score: {dkhp.knowledge_health_index:.2f}/100")
print(f"Orphan Rate: {dkhp.orphan_rate*100:.1f}%")
print(f"Structural Entropy: {dkhp.structural_entropy:.4f}")

# 3. Generate Subtractive Pruning Plan
pruner = SubtractivePruner(kg)
plan = pruner.generate_plan()
print(f"Interventions planned: {plan.total_actions}")
print(f"Projected Health: {plan.projected_health.knowledge_health_index:.2f}")
```

---

## 📊 Empirical Benchmarks & Reproducibility

This repository contains full replication packages for multi-repository longitudinal and factorial experiments:

```bash
# Generate synthetic benchmark vaults across 4 controlled conditions
python benchmarks/generator.py

# Reproduce paper Table 6 (DiD Estimation) and Table 7 (Factorial ANOVA)
python reproduction/generate_tables.py
```

### Key Empirical Findings:
* **$-34.2\%$** Structural entropy reduction via continuous metabolic homeostasis.
* **$-46.8\%$** Retrieval decision latency reduction in multi-hop agent tasks.
* **$+34.4\%$** Lift in factual grounding fidelity ($\ge 98.6\%$).

---

## 🧪 Testing

Run the automated test suite:

```bash
pytest tests/ -v
```

---

## 📜 Citation

If you use Cognitive Metabolism in your research or production systems, please cite:

```bibtex
@article{sung2026cognitivemetabolism,
  title={Cognitive Metabolism: A Dynamic Epistemological Framework for Knowledge Health, Structural Entropy Reduction, and Organizational Vitality},
  author={Sung, Ming-Hung and Sung, Shih-Yu},
  journal={Journal of Knowledge Management},
  year={2026},
  publisher={Emerald Publishing}
}
```

---

## ⚖️ License

Licensed under the [Apache License, Version 2.0](LICENSE).
