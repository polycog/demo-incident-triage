"""
Decision-process state: the confirmed record and policy settings, plus
the work in progress -- narrative text not yet read, pending steps still
to be checked by the LLM, and anything waiting on a human (LLM proposals,
typed commands).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cognition import DocEnum, EmpiricalConfidence, SelfReinitState

from .policy import PolicySettings, StepId, Tier, load_policy_settings
from .record import IncidentRecord

# ===


@dataclass(frozen=True)
class TierProposal:
    """The LLM's suggested tier, awaiting confirmation"""

    tier: Tier | None
    """suggested tier (``None`` if the model could not decide)"""

    agreement: EmpiricalConfidence | None
    """how many classification trials agreed"""

    @property
    def unanimous(self) -> bool:
        """All trials agreed"""

        return self.agreement is not None and float(self.agreement) == 1.0


@dataclass(frozen=True)
class ProgressReport:
    """What the LLM read from a narrative update, awaiting confirmation"""

    steps_done: tuple[StepId, ...] = ()
    """pending steps the text says were done"""


class Command(DocEnum):
    """Commands a user can type instead of a narrative update"""

    STATUS = "status", "show the full checklist"
    DONE = "done", "mark a step done by number, e.g. 'done 3'"
    UNDO = "undo", "mark a step not done, e.g. 'undo 3'"
    ESCALATE = "escalate", "the situation got worse: move to a higher tier"
    HELP = "help", "show these commands"
    QUIT = "quit", "end the session and save the incident log"


@dataclass(frozen=True)
class TypedCommand:
    """A parsed command line"""

    command: Command
    arg: str = ""

    @classmethod
    def parse(cls, line: str) -> TypedCommand | None:
        """A command, or ``None`` if the line is narrative text"""

        word, _, rest = line.strip().partition(" ")
        try:
            return cls(Command(word.lower()), rest.strip())
        except ValueError:
            return None


@dataclass
class TriageState(SelfReinitState):
    """
    State of the triage session.

    As a :class:`SelfReinitState`, the same instance survives each
    decision-process restart, so one cogent loop = one user turn.
    """

    policy: PolicySettings = field(default_factory=load_policy_settings)
    """values for the policy's [bracketed] placeholders"""

    record: IncidentRecord = field(default_factory=IncidentRecord)
    """confirmed facts only"""

    tier_proposal: TierProposal | None = None
    """LLM tier suggestion awaiting confirmation"""

    unread: list[str] = field(default_factory=list)
    """narrative text the LLM has not yet checked for progress"""

    unchecked_steps: dict[StepId, str] = field(default_factory=dict)
    """pending steps still to be checked, each with the text to check it against
    (non-empty while an update is being read)"""

    proposed_steps: list[StepId] = field(default_factory=list)
    """steps the LLM thinks were done, awaiting confirmation"""

    command: TypedCommand | None = None
    """command typed this turn"""

    closing: bool = False
    """the user asked to end the session"""

    shown_at: int = -1
    """timeline length when the checklist was last displayed"""
