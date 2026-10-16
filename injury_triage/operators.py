"""
The decision process: a set of independent WHEN/THEN operators.

Each cycle, every operator whose WHEN holds is proposed; the one with
the lowest :class:`Priority` value is applied. There is no hard-coded
flow -- "what happens next" falls out of the state. Generators
(``CheckStep``, ``ConfirmStepDone``) add one operator per pending item.
One user turn ends when an operator marked ``ends_turn`` runs
(``AdviseNextStep`` waits for input; ``CloseIncident`` ends the session).

The LLM is only consulted by ``ProposeTier`` (classify the tier) and
``CheckStep`` (was one pending step reported done?). Their output is held
as a proposal until ``ConfirmAgreedTier``, ``ConfirmDisputedTier`` or
``ConfirmStepDone`` gets a human yes/no (``ChooseTier`` lets the human
pick when there is no usable suggestion). Confirmed facts are never sent
back to the LLM.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime
from enum import IntEnum
from typing import Any, ClassVar, Self, cast

from cognition import IOContainer, Operator, OperatorGenerator
from rich.text import Text

from .console import AskChoice, AskText, AskYesNo, Say, TypedText, checklist, next_step_panel, tier_badge
from .language import LLMStepInterpreter, LLMTierInterpreter
from .policy import POLICY, Deadline, PolicySettings, StepId, Tier
from .record import EventKind, Source, StepStatus
from .reports import save_report
from .state import Command, TierProposal, TriageState, TypedCommand

# ===


class Priority(IntEnum):
    """When several operators apply, the lowest value wins"""

    READ = 1
    """finish checking an update, one item at a time, before asking about it"""

    CONFIRM = 2
    """then settle pending LLM proposals"""

    COMMAND = 3
    """then act on a command the user typed"""

    INTERPRET = 4
    """then let the LLM read new text"""

    CLOSE = 5
    """then end the session if everything is resolved"""

    ADVISE = 6
    """otherwise: say what to do next and wait for input"""


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class TriageOperator(Operator[TriageState]):
    """Base: named after the class, ranked by ``priority``"""

    priority: ClassVar[Priority]
    ends_turn: ClassVar[bool] = False

    def __init__(self) -> None:
        super().__init__(_snake(type(self).__name__), **({"terminal": True} if self.ends_turn else {}))

    def sort_key(self) -> tuple[int, int]:
        """Ranking used by the decision process (lower first)"""

        return (self.priority, 0)


# === io helpers (sensor: io.i.now; actuator: io.o.console)


def now(io: IOContainer) -> datetime:
    return cast(datetime, io.i.now)


def say(io: IOContainer, content: Any) -> None:
    io.o.console(Say(content))


def ask_yes_no(io: IOContainer, question: str) -> bool:
    return cast(bool, io.o.console(AskYesNo(question)))


def announce_tier(io: IOContainer, verb: str, tier: Tier, policy: PolicySettings) -> None:
    """Show the new tier; if its first step is immediate, show that step right away"""

    say(io, Text(f"{verb}: ").append(tier_badge(tier)))
    first = POLICY[tier].steps[0]
    if first.deadline is Deadline.IMMEDIATELY:
        say(io, Text(f"NOW: {first.text(policy)}", style=f"bold {tier.color}"))


###################################################
# Intake & tier
###################################################


class GatherDescription(TriageOperator):
    """
    WHEN: no description of the incident yet
    THEN: ask for an open description, including anything already done
    """

    priority = Priority.ADVISE

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return state.record.description is None

    def perform(self, state: TriageState, io: IOContainer) -> None:
        say(io, Text("If the student may be in danger, call 911 first.", style="bold red"))
        reply = cast(TypedText, io.o.console(AskText("Describe what happened, including anything already done")))
        if not reply.text:
            return

        state.record.description = reply.text
        state.record.started_at = now(io)
        state.record.note(reply.at, EventKind.NARRATIVE, reply.text)
        state.unread.append(reply.text)


class ProposeTier(TriageOperator):
    """
    WHEN: there is a description but no tier (and no suggestion yet)
    THEN: ask the LLM to suggest a tier (it classifies the description
          several times; each classification is one "reading")
    """

    priority = Priority.INTERPRET

    def __init__(self) -> None:
        super().__init__()
        self.interpreter = LLMTierInterpreter()

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return (
            state.record.description is not None
            and state.record.tier is None
            and state.tier_proposal is None
        )

    def perform(self, state: TriageState, io: IOContainer) -> None:
        say(io, Text("Reading the description...", style="dim"))
        try:
            state.tier_proposal = self.interpreter.classify_tier(cast(str, state.record.description))
        except Exception as e:  # pylint: disable=broad-exception-caught
            say(io, Text(f"(Could not get a suggestion: {e})", style="dim"))
            state.tier_proposal = TierProposal(None, None)


class ConfirmAgreedTier(TriageOperator):
    """
    WHEN: the LLM suggested a tier and all readings (repeated
          classifications of the description) agreed
    THEN: the user confirms it (or rejects it, and then picks one)
    """

    priority = Priority.CONFIRM

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        p = state.tier_proposal
        return p is not None and p.tier is not None and p.unanimous

    def perform(self, state: TriageState, io: IOContainer) -> None:
        proposal = cast(TierProposal, state.tier_proposal)
        tier = cast(Tier, proposal.tier)

        line = Text("Suggested: ").append(tier_badge(tier))
        if proposal.agreement is not None:
            a = proposal.agreement
            line.append(f"  ({a.selected}/{a.trials} readings agree)", style="dim")
        say(io, line)

        if ask_yes_no(io, f"Treat this as {tier.label}?"):
            state.tier_proposal = None
            state.record.set_tier(tier, now(io), Source.LLM_CONFIRMED)
            announce_tier(io, "Confirmed", tier, state.policy)
        else:  # drop the suggestion so ChooseTier applies next
            state.tier_proposal = TierProposal(None, proposal.agreement)


class ConfirmDisputedTier(TriageOperator):
    """
    WHEN: the LLM suggested a tier but the readings (repeated
          classifications of the description) disagreed
    THEN: warn, and the user confirms it (or rejects it, and then picks one)
    """

    priority = Priority.CONFIRM

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        p = state.tier_proposal
        return p is not None and p.tier is not None and not p.unanimous

    def perform(self, state: TriageState, io: IOContainer) -> None:
        proposal = cast(TierProposal, state.tier_proposal)
        tier = cast(Tier, proposal.tier)

        line = Text("Suggested: ").append(tier_badge(tier))
        if proposal.agreement is not None:
            a = proposal.agreement
            line.append(f"  ({a.selected}/{a.trials} readings agree)", style="dim")
        say(io, line)
        say(io, Text("I wasn't able to make a determination of severity, please provide one. If unsure, choose the higher tier.", style="yellow"))

        if ask_yes_no(io, f"Treat this as {tier.label}?"):
            state.tier_proposal = None
            state.record.set_tier(tier, now(io), Source.LLM_CONFIRMED)
            announce_tier(io, "Confirmed", tier, state.policy)
        else:  # drop the suggestion so ChooseTier applies next
            state.tier_proposal = TierProposal(None, proposal.agreement)


class ChooseTier(TriageOperator):
    """
    WHEN: there is no usable suggestion (the LLM could not decide,
          failed, or the user rejected its suggestion)
    THEN: the user picks the tier
    """

    priority = Priority.CONFIRM

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        p = state.tier_proposal
        return p is not None and p.tier is None

    def perform(self, state: TriageState, io: IOContainer) -> None:
        state.tier_proposal = None
        say(io, Text("If you're unsure between tiers, choose the higher one.", style="yellow"))
        choice = io.o.console(AskChoice("Which tier?", {str(t.number): t.label for t in Tier}))
        tier = next(t for t in Tier if str(t.number) == choice)
        state.record.set_tier(tier, now(io), Source.USER)
        announce_tier(io, "Confirmed", tier, state.policy)


###################################################
# Progress (LLM proposes, human confirms)
###################################################


class ReadProgress(TriageOperator):
    """
    WHEN: there is narrative text the LLM has not read yet
    THEN: start reading it: queue each still-pending step
          to be checked individually
    """

    priority = Priority.INTERPRET

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return state.record.tier is not None and bool(state.unread) and not state.unchecked_steps

    def perform(self, state: TriageState, io: IOContainer) -> None:
        text = "\n".join(state.unread)
        state.unread.clear()
        state.unchecked_steps = {s.id: text for s in state.record.pending()}
        say(io, Text("Checking for progress...", style="dim"))


def stop_reading(state: TriageState, io: IOContainer, error: Exception) -> None:
    """An LLM call failed: drop the rest of this reading"""

    say(io, Text(f"(Could not interpret that: {error}. You can use 'done <n>'.)", style="dim"))
    state.unchecked_steps.clear()


class CheckStep(OperatorGenerator[TriageState, LLMStepInterpreter]):
    """
    WHEN: a pending step has not been checked against the text being read
          (one operator per step)
    THEN: ask the LLM whether the text says that step is done
          (after the last check, say so if nothing was found)
    """

    priority: ClassVar[Priority] = Priority.READ

    def __init__(self, step_id: StepId, interpreter: LLMStepInterpreter) -> None:
        super().__init__(step=step_id.value)
        self.step_id = step_id
        self.interpreter = interpreter

    @classmethod
    def get_name(cls) -> str:
        return "check_step"

    @classmethod
    def generate(cls, state: TriageState, io: IOContainer, extra: LLMStepInterpreter) -> Iterable[Self]:
        yield from (cls(s, extra) for s in state.unchecked_steps)

    def sort_key(self) -> tuple[int, int]:
        return (self.priority, POLICY_NUMBER[self.step_id])  # earlier steps first

    def perform(self, state: TriageState, io: IOContainer) -> None:
        text = state.unchecked_steps.pop(self.step_id)
        tier = cast(Tier, state.record.tier)
        try:
            done = self.interpreter.step_done(text, tier, POLICY[tier].step(self.step_id))
        except Exception as e:  # pylint: disable=broad-exception-caught
            stop_reading(state, io, e)
            return
        if done:
            state.proposed_steps.append(self.step_id)
        if not state.unchecked_steps and not state.proposed_steps:
            say(io, Text("(No completed steps found in that update.)", style="dim"))


class ConfirmStepDone(OperatorGenerator[TriageState, None]):
    """
    WHEN: the LLM thinks a step was done (one operator per step)
    THEN: the user confirms or rejects it
    """

    priority: ClassVar[Priority] = Priority.CONFIRM

    def __init__(self, step_id: StepId) -> None:
        super().__init__(step=step_id.value)
        self.step_id = step_id

    @classmethod
    def get_name(cls) -> str:
        return "confirm_step_done"

    @classmethod
    def generate(cls, state: TriageState, io: IOContainer, extra: None) -> Iterable[Self]:
        yield from (cls(s) for s in state.proposed_steps)

    def sort_key(self) -> tuple[int, int]:
        return (self.priority, POLICY_NUMBER[self.step_id])  # earlier steps first

    def perform(self, state: TriageState, io: IOContainer) -> None:
        state.proposed_steps.remove(self.step_id)
        record = state.record
        step = next(s for s in record.protocol_steps if s.id is self.step_id)

        if ask_yes_no(io, f"It sounds like step {step.number} is done: \"{step.text(state.policy)}\" Correct?"):
            record.set_step(step, StepStatus.DONE, now(io), Source.LLM_CONFIRMED)
        else:
            record.note(now(io), EventKind.NOTE, f"Step {step.number} suggestion rejected by user")


POLICY_NUMBER: dict[StepId, int] = {s.id: s.number for p in POLICY.values() for s in p.steps}
"""step -> its number within its tier"""


###################################################
# Commands typed by the user
###################################################


def _typed(state: TriageState, *commands: Command) -> bool:
    return state.command is not None and state.command.command in commands


class ShowStatus(TriageOperator):
    """
    WHEN: the user typed 'status' or 'help'
    THEN: show the checklist / the command list
    """

    priority = Priority.COMMAND

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return _typed(state, Command.STATUS, Command.HELP)

    def perform(self, state: TriageState, io: IOContainer) -> None:
        cmd = cast(TypedCommand, state.command).command
        state.command = None
        if cmd is Command.HELP:
            say(io, "Type an update in your own words, or a command:")
            for c in Command:
                say(io, Text(f"  {c.value:<9} {c.__doc__}"))
        else:
            say(io, checklist(state.record, state.policy, now(io)))


class SetStepByNumber(TriageOperator):
    """
    WHEN: the user typed 'done <n>' or 'undo <n>'
    THEN: set that step directly (the user's word is the confirmation)
    """

    priority = Priority.COMMAND

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return _typed(state, Command.DONE, Command.UNDO)

    def perform(self, state: TriageState, io: IOContainer) -> None:
        typed = cast(TypedCommand, state.command)
        state.command = None
        record = state.record

        step = POLICY[cast(Tier, record.tier)].by_number(int(typed.arg)) if typed.arg.isdigit() else None
        if step is None:
            say(io, Text(f"Usage: {typed.command.value} <step number 1-{len(record.protocol_steps)}>", style="red"))
            return

        if typed.command is Command.DONE:
            record.set_step(step, StepStatus.DONE, now(io), Source.USER)
        else:
            record.set_step(step, StepStatus.PENDING, now(io), Source.USER, "undone")


class EscalateTier(TriageOperator):
    """
    WHEN: the user typed 'escalate' (the situation got worse)
    THEN: move to a higher tier, start its checklist, and re-read the
          narrative for steps of the new tier that are already done
    """

    priority = Priority.COMMAND

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return _typed(state, Command.ESCALATE)

    def perform(self, state: TriageState, io: IOContainer) -> None:
        state.command = None
        record = state.record
        current = cast(Tier, record.tier)

        higher = {str(t.number): t.label for t in Tier if t.more_severe_than(current)}
        if not higher:
            say(io, Text("Already at the highest tier.", style="red"))
            return

        choice = io.o.console(AskChoice("Escalate to which tier? (c = cancel)", higher | {"c": "cancel"}, "c"))
        if choice == "c":
            return

        tier = next(t for t in Tier if str(t.number) == choice)
        record.set_tier(tier, now(io), Source.USER)
        announce_tier(io, "Escalated", tier, state.policy)
        state.unread = [e.detail for e in record.timeline if e.kind is EventKind.NARRATIVE]


class EndSession(TriageOperator):
    """
    WHEN: the user typed 'quit'
    THEN: confirm if steps are still open, then close the session
    """

    priority = Priority.COMMAND

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return _typed(state, Command.QUIT)

    def perform(self, state: TriageState, io: IOContainer) -> None:
        state.command = None
        open_steps = len(state.record.pending())
        if not open_steps or ask_yes_no(io, f"{open_steps} step(s) still open. End the session anyway?"):
            state.closing = True


###################################################
# Each turn ends by closing or advising
###################################################


class CloseIncident(TriageOperator):
    """
    WHEN: every step is done, or the user chose to quit
    THEN: show the final checklist and save the incident log
    """

    priority = Priority.CLOSE
    ends_turn = True

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return state.closing or state.record.all_resolved

    def perform(self, state: TriageState, io: IOContainer) -> None:
        record = state.record
        record.closed_at = now(io)
        if record.tier is not None:
            say(io, checklist(record, state.policy, now(io)))
        path = save_report(record, state.policy)
        say(io, Text(f"Session closed. Incident log saved to {path}", style="bold"))


class AdviseNextStep(TriageOperator):
    """
    WHEN: the tier is known (fallback: nothing more urgent applies)
    THEN: show the checklist and the earliest unfinished step,
          then wait for an update or command
    """

    priority = Priority.ADVISE
    ends_turn = True

    def can_perform(self, state: TriageState, io: IOContainer) -> bool:
        return state.record.tier is not None

    def perform(self, state: TriageState, io: IOContainer) -> None:
        policy = state.policy
        if state.shown_at != len(state.record.timeline):  # only redraw after a change
            say(io, checklist(state.record, policy, now(io)))
            state.shown_at = len(state.record.timeline)
        say(io, next_step_panel(state.record, policy, now(io)))

        reply = cast(TypedText, io.o.console(AskText("Update (or 'help')")))
        if not reply.text:
            return

        state.command = TypedCommand.parse(reply.text)
        if state.command is None:
            state.record.note(reply.at, EventKind.NARRATIVE, reply.text)
            state.unread.append(reply.text)
