"""Synthetic & Controlled Knowledge Vault Generator for Benchmark Experiments."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List


class VaultGenerator:
    """Generates synthetic vaults corresponding to experimental conditions A, B, C, D."""

    @staticmethod
    def generate_vault(output_dir: str | Path, condition: str = "healthy", num_nodes: int = 100) -> Path:
        out_path = Path(output_dir) / condition
        out_path.mkdir(parents=True, exist_ok=True)

        # MOC Hub
        moc_content = f"""---
id: 00_MOC_Main
title: "00 MOC Master Map of Content"
tags: [moc, apex]
---

# 🗺️ Master Map of Content ({condition.upper()})

## Core Clusters
"""
        # Create core modules
        num_clusters = 5
        nodes_per_cluster = num_nodes // num_clusters

        for c in range(num_clusters):
            cluster_id = f"MOC_Cluster_{c:02d}"
            moc_content += f"- [[{cluster_id}|Cluster {c:02d}]]\n"
            
            # Write Cluster MOC
            c_content = f"""---
id: {cluster_id}
title: "Cluster {c:02d} Hub"
tags: [moc]
---

# Cluster {c:02d} Index
"""
            for i in range(nodes_per_cluster):
                node_id = f"Node_C{c:02d}_{i:03d}"
                c_content += f"- [[{node_id}|Knowledge Asset C{c}_{i}]]\n"
                
                # Node content based on condition
                if condition == "healthy":
                    # Well-connected, low redundancy, valid links
                    prev_node = f"Node_C{c:02d}_{max(0, i-1):03d}"
                    cross_node = f"Node_C{(c+1)%num_clusters:02d}_{i:03d}"
                    node_text = f"""---
id: {node_id}
title: "Knowledge Asset C{c:02d} {i:03d}"
tags: [concept, verified]
---

# {node_id}

This is a well-structured verified knowledge asset.
Parent: [[{cluster_id}]]
Related: [[{prev_node}]], [[{cross_node}]]
"""
                elif condition == "redundant":
                    # High redundancy, duplicated content and duplicate titles
                    node_text = f"""---
id: {node_id}
title: "Redundant Asset Duplicate"
tags: [unverified]
---

# {node_id}

Duplicated boilerplate text repeated across multiple files.
Parent: [[{cluster_id}]]
"""
                elif condition == "fragmented":
                    # Missing links, high orphan rate
                    node_text = f"""---
id: {node_id}
title: "Fragmented Asset {i:03d}"
tags: [scratch]
---

# {node_id}

Isolated thought with no incoming or outgoing links.
"""
                elif condition == "contradictory":
                    # Broken links and conflicting statements
                    node_text = f"""---
id: {node_id}
title: "Contradictory Asset {i:03d}"
tags: [conflict]
---

# {node_id}

Points to broken target: [[NonExistentTarget_{i:03d}]].
Contradicts rules in [[{cluster_id}]].
"""
                else:
                    node_text = f"# {node_id}\nContent."

                with open(out_path / f"{node_id}.md", "w", encoding="utf-8") as f:
                    f.write(node_text)

            with open(out_path / f"{cluster_id}.md", "w", encoding="utf-8") as f:
                f.write(c_content)

        with open(out_path / "00_MOC_Main.md", "w", encoding="utf-8") as f:
            f.write(moc_content)

        return out_path


def main():
    base_dir = Path(__file__).parent / "sample_vault"
    for cond in ["healthy", "redundant", "fragmented", "contradictory"]:
        p = VaultGenerator.generate_vault(base_dir, condition=cond, num_nodes=50)
        print(f"[+] Generated benchmark vault: {p}")


if __name__ == "__main__":
    main()
