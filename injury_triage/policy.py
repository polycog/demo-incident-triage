"""
The student injury policy (triage section), encoded as data.

Everything the app knows about the policy lives here: the tiers and
their criteria, the deadlines, the ordered steps for each tier, and the
``[policy]`` settings from config.toml that fill the [bracketed] values
in the policy text. Operators and prompts are derived from these
definitions; nothing about the policy is hard-coded elsewhere.

Docstrings on enum members are not just comments -- the cognition
language tools (EnumClassifier, ModelPopulator) put them into the
LLM prompts, so they are written as definitions.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from enum import StrEnum
from string import Template

from cognition import DocEnum
from pydantic import BaseModel, Field

from .config import load_config

# ===


class PolicySettings(BaseModel):
    """Values for the [bracketed] placeholders in the policy"""

    district_office: str = Field("district office", description="[district office]")
    district_notice_hours: float = Field(1, gt=0, description="[1 hour]")
    tier1_report_hours: float = Field(24, gt=0, description="[24 hours]")
    tier2_report_deadline: str = Field(
        "end of next school day",
        description="[end of next school day]; due time is computed as the next weekday at school_day_end",
    )
    parent_notice_method: str = Field("note / call / app", description="[note / call / app]")
    school_day_end: time = Field(time(15, 30), description="used for 'end of school day'")

    def template_values(self) -> dict[str, str]:
        """``$placeholder`` values used in step instructions"""

        return {
            "district_office": self.district_office,
            "district_notice": _hours(self.district_notice_hours),
            "tier1_report": _hours(self.tier1_report_hours),
            "tier2_report": self.tier2_report_deadline,
            "parent_notice_method": self.parent_notice_method,
        }


def load_policy_settings() -> PolicySettings:
    """The ``[policy]`` table of config.toml (defaults for anything missing)"""

    return PolicySettings.model_validate(load_config().get("policy", {}))


def _hours(h: float) -> str:
    n = int(h) if float(h).is_integer() else h
    return f"{n} hour" if n == 1 else f"{n} hours"


class Tier(DocEnum):
    """
    Severity tier of a student injury.
    If unsure between two tiers, choose the higher (more severe) one.
    """

    EMERGENCY = (
        "emergency",
        "Tier 1, life-threatening or possibly so: unresponsive, trouble breathing, "
        "severe bleeding, suspected neck or spine injury, seizure, "
        "severe allergic reaction, obvious major fracture",
    )
    SIGNIFICANT = (
        "significant",
        "Tier 2, needs evaluation or outside care: any head injury, "
        "possible fracture or sprain, wound that may need stitches, "
        "eye or dental injury, student can't return to class",
    )
    MINOR = (
        "minor",
        "Tier 3, first aid only: small scrape, minor bruise, "
        "nosebleed that stops, student returns to class",
    )

    @property
    def number(self) -> int:
        """1 (most severe) to 3 (least severe)"""

        return list(Tier).index(self) + 1

    @property
    def label(self) -> str:
        """Short heading, e.g. 'Tier 1: Emergency'"""

        return f"Tier {self.number}: {self.name.title()}"

    @property
    def color(self) -> str:
        """Display color: red / yellow / green"""

        return {
            Tier.EMERGENCY: "red",
            Tier.SIGNIFICANT: "yellow",
            Tier.MINOR: "green",
        }[self]

    def more_severe_than(self, other: Tier) -> bool:
        """``True`` if this tier is higher priority than ``other``"""

        return self.number < other.number


class Deadline(StrEnum):
    """When a step must be completed, relative to the start of the incident"""

    IMMEDIATELY = "right away"
    BEFORE_RELEASE = "before the student returns to class or leaves"
    SAME_DAY = "same day"
    DISTRICT_NOTICE_WINDOW = "within the district-notification window"
    TIER1_REPORT_WINDOW = "within the Tier 1 report window"
    END_OF_NEXT_SCHOOL_DAY = "by end of next school day"

    def due(self, start: datetime, policy: PolicySettings) -> datetime | None:
        """
        Clock time this deadline falls at (``None`` if it is event-based)

        :param start: when the incident was reported in the app
        :param policy: configured policy values
        """

        match self:
            case Deadline.IMMEDIATELY:
                return start
            case Deadline.BEFORE_RELEASE:
                return None
            case Deadline.SAME_DAY:
                return datetime.combine(start.date(), time(23, 59), start.tzinfo)
            case Deadline.DISTRICT_NOTICE_WINDOW:
                return start + timedelta(hours=policy.district_notice_hours)
            case Deadline.TIER1_REPORT_WINDOW:
                return start + timedelta(hours=policy.tier1_report_hours)
            case Deadline.END_OF_NEXT_SCHOOL_DAY:
                day = start.date() + timedelta(days=1)
                while day.weekday() >= 5:  # skip Saturday/Sunday
                    day += timedelta(days=1)
                return datetime.combine(day, policy.school_day_end, start.tzinfo)


class StepId(DocEnum):
    """
    Every action in the policy. Each docstring states what it means
    for the step to be DONE; the LLM uses it to read progress updates.
    """

    # Tier 1
    CALL_911 = "call_911", "911 (EMS) has been called"
    START_EMERGENCY_CARE = (
        "start_emergency_care",
        "first aid, CPR/AED, or emergency medication (e.g. EpiPen) has been started",
    )
    NOTIFY_NURSE_AND_ADMIN = (
        "notify_nurse_and_admin",
        "BOTH the school nurse and an administrator have been notified",
    )
    ADMIN_CALLS_PARENT = (
        "admin_calls_parent",
        "an administrator has called the student's parent or guardian",
    )
    NOTIFY_DISTRICT = "notify_district", "the district office has been notified"
    FILE_REPORT_TIER1 = "file_report_tier1", "the injury report has been filed"

    # Tier 2
    NURSE_EVALUATES = (
        "nurse_evaluates",
        "the school nurse has evaluated the student",
    )
    CALL_PARENT = "call_parent", "the student's parent or guardian has been called"
    INFORM_ADMIN = "inform_admin", "an administrator has been informed"
    FILE_REPORT_TIER2 = "file_report_tier2", "the injury report has been filed"

    # Tier 3
    GIVE_FIRST_AID = "give_first_aid", "first aid has been given"
    RECORD_NURSE_LOG = (
        "record_nurse_log",
        "the visit has been recorded in the nurse visit log",
    )
    NOTIFY_PARENT_SAME_DAY = (
        "notify_parent_same_day",
        "the parent or guardian has been notified (note, call, or app)",
    )


class PolicyStep(BaseModel, frozen=True):
    """One numbered step of a tier's protocol"""

    id: StepId = Field(description="which action this is")
    number: int = Field(description="position within the tier (1 = first)")
    instruction: str = Field(
        description="policy wording; $placeholders are filled from config"
    )
    deadline: Deadline | None = Field(default=None, description="when it is due")

    def text(self, policy: PolicySettings) -> str:
        """Policy wording with the configured values filled in"""

        return Template(self.instruction).substitute(policy.template_values())


class TierProtocol(BaseModel, frozen=True):
    """A tier and the ordered steps the policy requires for it"""

    tier: Tier
    steps: tuple[PolicyStep, ...]

    def step(self, step_id: StepId) -> PolicyStep:
        """Look up a step of this protocol"""

        return next(s for s in self.steps if s.id is step_id)

    def by_number(self, number: int) -> PolicyStep | None:
        """Look up a step by its displayed number"""

        return next((s for s in self.steps if s.number == number), None)


# ===


def _steps(*specs: tuple[StepId, str, Deadline | None]) -> tuple[PolicyStep, ...]:
    return tuple(
        PolicyStep(id=i, number=n, instruction=t, deadline=d)
        for n, (i, t, d) in enumerate(specs, start=1)
    )


POLICY: dict[Tier, TierProtocol] = {
    Tier.EMERGENCY: TierProtocol(
        tier=Tier.EMERGENCY,
        steps=_steps(
            (StepId.CALL_911, "Call 911 right away. Don't wait for an administrator.", Deadline.IMMEDIATELY),
            (StepId.START_EMERGENCY_CARE, "Start first aid, CPR/AED, or emergency meds per protocol.", Deadline.IMMEDIATELY),
            (StepId.NOTIFY_NURSE_AND_ADMIN, "Notify nurse and administrator.", Deadline.IMMEDIATELY),
            (StepId.ADMIN_CALLS_PARENT, "Administrator calls parent immediately.", Deadline.IMMEDIATELY),
            (StepId.NOTIFY_DISTRICT, "Notify $district_office within $district_notice.", Deadline.DISTRICT_NOTICE_WINDOW),
            (StepId.FILE_REPORT_TIER1, "Report filed within $tier1_report.", Deadline.TIER1_REPORT_WINDOW),
        ),
    ),
    Tier.SIGNIFICANT: TierProtocol(
        tier=Tier.SIGNIFICANT,
        steps=_steps(
            (StepId.NURSE_EVALUATES, "Nurse evaluates the student.", None),
            (StepId.CALL_PARENT, "Call parent before student returns to class or leaves.", Deadline.BEFORE_RELEASE),
            (StepId.INFORM_ADMIN, "Inform administrator same day.", Deadline.SAME_DAY),
            (StepId.FILE_REPORT_TIER2, "Report filed by $tier2_report.", Deadline.END_OF_NEXT_SCHOOL_DAY),
        ),
    ),
    Tier.MINOR: TierProtocol(
        tier=Tier.MINOR,
        steps=_steps(
            (StepId.GIVE_FIRST_AID, "Give first aid.", None),
            (StepId.RECORD_NURSE_LOG, "Record in nurse visit log.", None),
            (StepId.NOTIFY_PARENT_SAME_DAY, "Notify parent same day by $parent_notice_method.", Deadline.SAME_DAY),
        ),
    ),
}
"""The triage policy: tier -> ordered protocol"""
