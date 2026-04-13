"""
Convert graphify graph.json → Obsidian vault (markdown notes with [[wikilinks]]).

Run from the project root:
    python3 graphify-out/gen_obsidian.py

Output: graphify-out/obsidian-vault/
Open that folder as a vault in Obsidian, then open Graph View (Ctrl+G).
"""

import json
import re
from pathlib import Path

GRAPH_JSON = Path(__file__).parent / "graph.json"
VAULT = Path(__file__).parent / "obsidian-vault"
VAULT.mkdir(exist_ok=True)

with GRAPH_JSON.open() as f:
    data = json.load(f)

nodes = {n["id"]: n for n in data["nodes"]}
links = data.get("links", [])

# Build adjacency: source_id → list of (target_id, relation)
outgoing: dict[str, list[tuple[str, str]]] = {}
incoming: dict[str, list[tuple[str, str]]] = {}
for lnk in links:
    src, tgt, rel = lnk["source"], lnk["target"], lnk.get("relation", "related")
    outgoing.setdefault(src, []).append((tgt, rel))
    incoming.setdefault(tgt, []).append((src, rel))


def safe_filename(label: str) -> str:
    """Turn a label into a safe markdown filename."""
    name = re.sub(r'[\\/:*?"<>|]', "_", label)
    return name[:100]  # Obsidian handles long names fine but let's be safe


# Build a map: node_id → filename (without .md)
id_to_fname: dict[str, str] = {}
fname_count: dict[str, int] = {}
for nid, node in nodes.items():
    base = safe_filename(node["label"])
    count = fname_count.get(base, 0)
    fname_count[base] = count + 1
    id_to_fname[nid] = base if count == 0 else f"{base}_{count}"


def wikilink(node_id: str) -> str:
    fname = id_to_fname.get(node_id)
    if fname:
        label = nodes[node_id]["label"]
        return f"[[{fname}|{label}]]"
    return node_id


written = 0
for nid, node in nodes.items():
    fname = id_to_fname[nid]
    lines = [
        f"# {node['label']}",
        "",
        f"- **Type:** {node.get('file_type', 'unknown')}",
        f"- **Source:** `{node.get('source_file', '')}` {node.get('source_location', '')}",
        f"- **Community:** {node.get('community', '?')}",
        "",
    ]

    outs = outgoing.get(nid, [])
    if outs:
        lines.append("## Outgoing")
        for tgt_id, rel in outs:
            lines.append(f"- `{rel}` → {wikilink(tgt_id)}")
        lines.append("")

    ins = incoming.get(nid, [])
    if ins:
        lines.append("## Incoming")
        for src_id, rel in ins:
            lines.append(f"- {wikilink(src_id)} → `{rel}`")
        lines.append("")

    (VAULT / f"{fname}.md").write_text("\n".join(lines), encoding="utf-8")
    written += 1

# Write an index note
community_groups: dict[int, list[str]] = {}
for nid, node in nodes.items():
    c = node.get("community", -1)
    community_groups.setdefault(c, []).append(nid)

idx_lines = ["# Graph Index", "", f"**{written} nodes · {len(links)} links**", ""]
for c_id in sorted(community_groups):
    members = community_groups[c_id]
    idx_lines.append(f"## Community {c_id} ({len(members)} nodes)")
    for nid in sorted(members, key=lambda x: nodes[x]["label"]):
        idx_lines.append(f"- {wikilink(nid)}")
    idx_lines.append("")

(VAULT / "INDEX.md").write_text("\n".join(idx_lines), encoding="utf-8")

print(f"Done. Wrote {written} notes + INDEX.md to {VAULT}")
print("Next: open graphify-out/obsidian-vault/ as a vault in Obsidian, then press Ctrl+G.")
