"""
Saving the incident log (a draft to support the actual report), as
``.md`` and ``.json``, in ``reports_dir`` from config.toml.
"""

from __future__ import annotations

from pathlib import Path

from .config import load_config
from .policy import PolicySettings
from .record import IncidentRecord

REPORTS_DIR = Path(load_config().get("reports_dir", "reports"))
"""where incident logs are saved (``reports_dir`` in config.toml)"""


def to_markdown(record: IncidentRecord, policy: PolicySettings) -> str:
    """Human-readable incident log"""

    def ts(d: object) -> str:
        return d.strftime("%Y-%m-%d %H:%M:%S") if d else "-"  # type: ignore[attr-defined]

    lines = [
        "# Student injury: triage log (draft)",
        "",
        f"- Started: {ts(record.started_at)}",
        f"- Closed: {ts(record.closed_at)}",
        f"- Tier: {record.tier.label if record.tier else 'not set'}",
    ]
    if record.previous_tiers:
        lines.append(f"- Escalated from: {', '.join(t.label for t in record.previous_tiers)}")

    lines += ["", "## Description", "", record.description or "-", "", "## Checklist", ""]
    for step in record.protocol_steps:
        rec = record.steps[step.id]
        when = f" ({ts(rec.at)}; {rec.source})" if rec.at and rec.source else ""
        lines.append(f"{step.number}. [{rec.status}] {step.text(policy)}{when}")

    lines += ["", "## Timeline", ""]
    lines += [f"- {ts(e.at)} [{e.kind}] {e.detail}" for e in record.timeline]

    lines += ["", "_This log records what the user confirmed; it is not the official report._", ""]
    return "\n".join(lines)


def save_report(record: IncidentRecord, policy: PolicySettings) -> Path:
    """Write ``.md`` (readable) and ``.json`` (structured); return the .md path"""

    stamp = (record.started_at or record.closed_at)
    name = f"incident-{stamp:%Y%m%d-%H%M%S}" if stamp else "incident"

    out = REPORTS_DIR
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(record.model_dump_json(indent=2))
    md = out / f"{name}.md"
    md.write_text(to_markdown(record, policy))
    return md
