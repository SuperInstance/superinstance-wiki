#!/usr/bin/env python3
"""
Repo Metrics Automator — Zero API calls.
Parses existing triage markdown files and computes health scores.
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Scoring weights (from spec)
# ---------------------------------------------------------------------------
RELEVANCE_WEIGHT = {
    "Core Fleet": 1.0,
    "Named Vessel": 0.9,
    "Integration Bridge": 0.8,
    "Experimental": 0.7,
    "Chronicled": 0.6,
    "Fork": 0.6,
    "Orphan": 0.5,
}

COMPLETENESS_WEIGHT = {
    "Production": 1.0,
    "Functional": 0.7,
    "Skeleton": 0.4,
    "Scaffold": 0.2,
}

LIFECYCLE_SCORE = {
    "Active Dev": 1.0,
    "Maintenance": 0.7,
    "Dormant": 0.4,
    "Abandoned": 0.2,
}

STRATEGIC_BONUS = {
    "KEEP": +10,
    "PRIVATE": 0,
    "ARCHIVE": -20,
    "MONITOR": 0,
    "REVIEW": 0,
}

TIER_LABELS = [
    (90, "Platinum"),
    (75, "Gold"),
    (50, "Silver"),
    (25, "Bronze"),
    (0, "Rust"),
]


def parse_markdown_table(text: str) -> list[dict]:
    """Parse a markdown table into a list of dicts."""
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|")]
    if len(table_lines) < 2:
        return []
    header_line = table_lines[0]
    headers = [h.strip() for h in header_line.strip("|").split("|")]
    headers = [h for h in headers if h]
    rows = []
    for line in table_lines[1:]:
        # Skip separator line: consists only of | - : and spaces
        if all(c in "|-: \t" for c in line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        cells = cells[:len(headers)]
        if len(cells) < len(headers):
            continue
        row = {headers[i]: cells[i] for i in range(len(headers))}
        rows.append(row)
    return rows


def read_index(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = []
    current_section = ""
    current_lines = []
    for line in lines:
        m = re.match(r"^##\s+(.+)", line)
        if m:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
                current_lines = []
            current_section = m.group(1).strip()
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_section, "\n".join(current_lines)))

    all_rows = []
    for section_name, section_text in sections:
        rows = parse_markdown_table(section_text)
        for r in rows:
            r["_section"] = section_name
        all_rows.extend(rows)
    return all_rows


def normalize_repo_name(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def build_repo_db(index_dir: Path) -> dict:
    files = {
        "relevance": "FLEET-RELEVANCE.md",
        "completeness": "COMPLETENESS-TIER.md",
        "lifecycle": "LIFECYCLE-STAGE.md",
        "action": "STRATEGIC-ACTION.md",
    }
    db = {}
    for key, fname in files.items():
        rows = read_index(index_dir / fname)
        for row in rows:
            name = row.get("Repo", "").strip()
            if not name:
                continue
            norm = normalize_repo_name(name)
            if norm not in db:
                db[norm] = {"repo": name, "sources": set()}
            # Merge all non-metadata fields
            for k, v in row.items():
                if k.startswith("_"):
                    continue
                if v.strip():
                    db[norm][k] = v.strip()
            db[norm]["sources"].add(key)
    return db


def compute_score(repo: dict) -> dict:
    relevance = repo.get("Relevance", "Orphan")
    tier = repo.get("Tier", "Scaffold")
    lifecycle = repo.get("Lifecycle", "Abandoned")
    action = repo.get("Action", "REVIEW")

    r_w = RELEVANCE_WEIGHT.get(relevance, 0.5)
    c_w = COMPLETENESS_WEIGHT.get(tier, 0.2)
    l_s = LIFECYCLE_SCORE.get(lifecycle, 0.2)
    s_b = STRATEGIC_BONUS.get(action, 0)

    base = (r_w * 0.35 + c_w * 0.35 + l_s * 0.30) * 100
    score = min(100, max(0, base + s_b))

    label = "Rust"
    for threshold, lbl in TIER_LABELS:
        if score >= threshold:
            label = lbl
            break

    return {
        "relevance": relevance,
        "completeness_tier": tier,
        "lifecycle": lifecycle,
        "strategic_action": action,
        "relevance_weight": r_w,
        "completeness_weight": c_w,
        "lifecycle_score": l_s,
        "strategic_bonus": s_b,
        "base_score": round(base, 2),
        "score": round(score, 2),
        "tier_label": label,
    }


def generate_json(db: dict) -> dict:
    metrics = {}
    for norm, repo in db.items():
        if len(repo.get("sources", set())) < 2:
            continue
        metrics[norm] = {
            "repo": repo["repo"],
            "metrics": compute_score(repo),
        }
    sorted_metrics = dict(sorted(metrics.items(), key=lambda x: x[1]["metrics"]["score"], reverse=True))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_repos": len(sorted_metrics),
        "formula": {
            "description": "base = (relevance*0.35 + completeness*0.35 + lifecycle*0.30) * 100; score = min(100, max(0, base + strategic_bonus))",
            "relevance_weights": RELEVANCE_WEIGHT,
            "completeness_weights": COMPLETENESS_WEIGHT,
            "lifecycle_scores": LIFECYCLE_SCORE,
            "strategic_bonuses": STRATEGIC_BONUS,
        },
        "repos": sorted_metrics,
    }


def generate_dashboard(metrics: dict) -> str:
    repos = metrics["repos"]
    total = len(repos)
    tier_counts = {}
    for data in repos.values():
        lbl = data["metrics"]["tier_label"]
        tier_counts[lbl] = tier_counts.get(lbl, 0) + 1

    lines = [
        "# Repo Metrics Dashboard",
        "",
        f"**Generated:** {metrics['generated_at']}",
        f"**Total Repos:** {total}",
        "",
        "## Formula",
        "",
        "```",
        "base = (relevance_weight * 0.35 + completeness_weight * 0.35 + lifecycle_score * 0.30) * 100",
        "score = min(100, max(0, base + strategic_bonus))",
        "```",
        "",
        "### Relevance Weights",
        "",
        "| Relevance | Weight |",
        "|-----------|--------|",
    ]
    for k, v in RELEVANCE_WEIGHT.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("### Completeness Weights")
    lines.append("")
    lines.append("| Completeness | Weight |")
    lines.append("|--------------|--------|")
    for k, v in COMPLETENESS_WEIGHT.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("### Lifecycle Scores")
    lines.append("")
    lines.append("| Lifecycle | Score |")
    lines.append("|-----------|-------|")
    for k, v in LIFECYCLE_SCORE.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("### Strategic Bonuses")
    lines.append("")
    lines.append("| Action | Bonus |")
    lines.append("|--------|-------|")
    for k, v in STRATEGIC_BONUS.items():
        lines.append(f"| {k} | {v:+d} |")
    lines.append("")

    lines.extend([
        "## Tier Distribution",
        "",
        "| Tier | Count | % |",
        "|------|-------|---|",
    ])
    for lbl in ["Platinum", "Gold", "Silver", "Bronze", "Rust"]:
        c = tier_counts.get(lbl, 0)
        pct = round(c / total * 100, 1) if total else 0
        lines.append(f"| {lbl} | {c} | {pct}% |")
    lines.append("")

    lines.extend([
        "## Top 25 Repos",
        "",
        "| Rank | Repo | Score | Tier | Relevance | Completeness | Lifecycle | Action |",
        "|------|------|-------|------|-----------|--------------|-----------|--------|",
    ])
    for i, (norm, data) in enumerate(list(repos.items())[:25], 1):
        m = data["metrics"]
        lines.append(
            f"| {i} | {data['repo']} | {m['score']} | {m['tier_label']} | "
            f"{m['relevance']} | {m['completeness_tier']} | {m['lifecycle']} | {m['strategic_action']} |"
        )
    lines.append("")

    lines.extend([
        "## Bottom 10 Repos",
        "",
        "| Rank | Repo | Score | Tier | Relevance | Completeness | Lifecycle | Action |",
        "|------|------|-------|------|-----------|--------------|-----------|--------|",
    ])
    for i, (norm, data) in enumerate(list(repos.items())[-10:], total - 9):
        m = data["metrics"]
        lines.append(
            f"| {i} | {data['repo']} | {m['score']} | {m['tier_label']} | "
            f"{m['relevance']} | {m['completeness_tier']} | {m['lifecycle']} | {m['strategic_action']} |"
        )
    lines.append("")

    lines.extend([
        "## Sample Breakdowns",
        "",
    ])
    samples = list(repos.items())[:5]
    for norm, data in samples:
        m = data["metrics"]
        lines.extend([
            f"### {data['repo']}",
            "",
            f"- **Score:** {m['score']}",
            f"- **Tier:** {m['tier_label']}",
            f"- **Relevance:** {m['relevance']} (weight {m['relevance_weight']})",
            f"- **Completeness:** {m['completeness_tier']} (weight {m['completeness_weight']})",
            f"- **Lifecycle:** {m['lifecycle']} (score {m['lifecycle_score']})",
            f"- **Action:** {m['strategic_action']} (bonus {m['strategic_bonus']:+d})",
            f"- **Base:** {m['base_score']}",
            "",
        ])

    lines.append("---")
    lines.append("*Generated by scripts/repo_metrics.py*")
    return "\n".join(lines)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    index_dir = repo_root / "INDEXES"
    data_dir = repo_root / "data"
    data_dir.mkdir(exist_ok=True)

    db = build_repo_db(index_dir)
    metrics = generate_json(db)

    json_path = data_dir / "repo-metrics.json"
    json_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    dashboard = generate_dashboard(metrics)
    dash_path = repo_root / "METRICS-DASHBOARD.md"
    dash_path.write_text(dashboard, encoding="utf-8")

    print(f"Wrote {json_path} ({metrics['total_repos']} repos)")
    print(f"Wrote {dash_path}")


if __name__ == "__main__":
    main()
