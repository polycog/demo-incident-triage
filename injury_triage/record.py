"""
The incident record: everything a person has CONFIRMED.

LLM output never lands here directly. It is first held as a proposal
(see ``state.py``) and only written to the record after a human says yes.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .policy import POLICY, PolicyStep, StepId, Tier

# ===


class StepStatus(StrEnum):
    """Progress of a single policy step"""

    PENDING = "pending"
    """not yet done"""

    DONE = "done"
    """confirmed done"""


class Source(StrEnum):
    """How a confirmed fact was established"""

    LLM_CONFIRMED = "suggested by the assistant, confirmed by the user"
    USER = "entered or chosen directly by the user"


class EventKind(StrEnum):
    """Categories of timeline entries"""

    NARRATIVE = "narrative"
    TIER = "tier"
    STEP = "step"
    NOTE = "note"


class Event(BaseModel):
    """One timestamped entry in the incident timeline"""

    at: datetime
    kind: EventKind
    detail: str


class StepRecord(BaseModel):
    """Current status of one step, and when/how it was set"""

    status: StepStatus = StepStatus.PENDING
    at: datetime | None = None
    source: Source | None = None


class IncidentRecord(BaseModel):
    """Confirmed facts about one incident"""

    started_at: datetime | None = Field(None, description="when the description was entered")
    description: str | None = Field(None, description="the initial open description")
    tier: Tier | None = Field(None, description="confirmed tier")
    previous_tiers: list[Tier] = Field(default_factory=list, description="tiers before escalation")
    steps: dict[StepId, StepRecord] = Field(default_factory=dict, description="checklist for the tier")
    timeline: list[Event] = Field(default_factory=list)
    closed_at: datetime | None = None

    # === checklist queries

    @property
    def protocol_steps(self) -> tuple[PolicyStep, ...]:
        """The confirmed tier's steps, in policy order"""

        return POLICY[self.tier].steps if self.tier else ()

    def status(self, step: PolicyStep) -> StepStatus:
        """Status of a step"""

        return self.steps[step.id].status

    def pending(self) -> list[PolicyStep]:
        """Steps not yet done, in policy order"""

        return [s for s in self.protocol_steps if self.status(s) is StepStatus.PENDING]

    def next_step(self) -> PolicyStep | None:
        """The earliest step that is not done -- even if later ones are"""

        pending = self.pending()
        return pending[0] if pending else None

    def skipped(self) -> list[PolicyStep]:
        """Pending steps that come before a step already done"""

        done_numbers = [
            s.number for s in self.protocol_steps if self.status(s) is StepStatus.DONE
        ]
        last_done = max(done_numbers, default=0)
        return [s for s in self.pending() if s.number < last_done]

    @property
    def all_resolved(self) -> bool:
        """Every step is done"""

        return self.tier is not None and not self.pending()

    @property
    def closed(self) -> bool:
        """Session has ended"""

        return self.closed_at is not None

    # === confirmed changes (each also adds a timeline entry)

    def note(self, at: datetime, kind: EventKind, detail: str) -> None:
        """Add a timeline entry"""

        self.timeline.append(Event(at=at, kind=kind, detail=detail))

    def set_tier(self, tier: Tier, at: datetime, source: Source) -> None:
        """Confirm the tier and start that tier's checklist"""

        if self.tier is not None:
            self.previous_tiers.append(self.tier)
        self.tier = tier
        self.steps = {s.id: StepRecord() for s in POLICY[tier].steps}
        self.note(at, EventKind.TIER, f"{tier.label} ({source})")

    def set_step(self, step: PolicyStep, status: StepStatus, at: datetime, source: Source, why: str = "") -> None:
        """Record a step's status"""

        self.steps[step.id] = StepRecord(status=status, at=at, source=source)
        suffix = f" -- {why}" if why else ""
        self.note(at, EventKind.STEP, f"Step {step.number} {status}: {step.id.value}{suffix}")
