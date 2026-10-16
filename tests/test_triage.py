"""
Offline tests: a scripted console and a fake interpreter stand in
for the human and the LLM, so the decision process is exercised
deterministically. The fake answers from canned readings keyed by the
text being read.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from cognition import Actuator, EmpiricalConfidence
from rich.console import Console

from injury_triage.agent import build_agent, run
from injury_triage.console import AskChoice, AskText, AskYesNo, Say, TypedText
from injury_triage.policy import POLICY, Deadline, PolicySettings, PolicyStep, StepId, Tier
from injury_triage.record import EventKind, Source, StepStatus
from injury_triage.state import ProgressReport, TierProposal

T0 = datetime(2026, 10, 15, 10, 0)  # a Thursday


class ScriptedConsole(Actuator[object, object]):
    """Answers prompts from a script; fails if a prompt wasn't expected"""

    def __init__(self, *answers: object) -> None:
        self.answers = deque(answers)
        self.prompts: list[object] = []
        self.render = Console(record=True, width=120)

    @property
    def name(self) -> str:
        return "console"

    def actuate(self, param: object) -> object:
        if isinstance(param, Say):
            self.render.print(param.content)
            return None
        assert isinstance(param, AskText | AskYesNo | AskChoice)
        self.prompts.append(param)
        assert self.answers, f"unexpected prompt: {param}"
        answer = self.answers.popleft()
        return TypedText(answer, T0) if isinstance(param, AskText) else answer

    @property
    def text(self) -> str:
        return self.render.export_text(clear=False)


class FakeInterpreter:
    """
    Stands in for all interpreters: answers from canned readings
    (keyed by the text being read); records what it was asked
    """

    def __init__(self, tier: Tier | None, readings: dict[str, ProgressReport] | None = None, agree: int = 3) -> None:
        self.tier = tier
        self.agree = agree
        self.readings = readings or {}
        self.step_calls: list[tuple[str, StepId]] = []

    def classify_tier(self, description: str) -> TierProposal:
        return TierProposal(self.tier, EmpiricalConfidence(self.agree, 3))

    def step_done(self, text: str, tier: Tier, step: PolicyStep) -> bool:
        self.step_calls.append((text, step.id))
        return step.id in self.readings.get(text, ProgressReport()).steps_done


def play(interpreter: FakeInterpreter, *answers: object, tmp_path):
    console = ScriptedConsole(*answers)
    with (
        patch("injury_triage.operators.LLMTierInterpreter", return_value=interpreter),
        patch("injury_triage.agent.LLMStepInterpreter", return_value=interpreter),
    ):
        agent = build_agent(console, clock=lambda: T0)
    with patch("injury_triage.reports.REPORTS_DIR", tmp_path):
        state = run(agent)
    assert not console.answers, f"unused answers: {list(console.answers)}"
    return state, console


def statuses(state) -> list[StepStatus]:
    return [state.record.status(s) for s in state.record.protocol_steps]


# ===


def test_policy_is_well_formed():
    for tier, protocol in POLICY.items():
        assert protocol.tier is tier
        assert [s.number for s in protocol.steps] == list(range(1, len(protocol.steps) + 1))
        for s in protocol.steps:
            s.text(PolicySettings())  # every $placeholder has a config value
    assert Tier.EMERGENCY.more_severe_than(Tier.SIGNIFICANT)
    assert [t.color for t in Tier] == ["red", "yellow", "green"]


def test_deadlines_use_config():
    p = PolicySettings()
    assert Deadline.DISTRICT_NOTICE_WINDOW.due(T0, p) == T0 + timedelta(hours=1)
    assert Deadline.TIER1_REPORT_WINDOW.due(T0, p) == T0 + timedelta(hours=24)
    friday = datetime(2026, 10, 16, 10, 0)
    assert Deadline.END_OF_NEXT_SCHOOL_DAY.due(friday, p) == datetime(2026, 10, 19, 15, 30)  # Monday


def test_tier2_with_confirmations(tmp_path):
    llm = FakeInterpreter(Tier.SIGNIFICANT, {
        "Fell and hit head on the slide; nurse checked her":
            ProgressReport(steps_done=(StepId.NURSE_EVALUATES,)),
        "called mom and told the principal":
            ProgressReport(steps_done=(StepId.CALL_PARENT, StepId.INFORM_ADMIN)),
    })
    state, console = play(
        llm,
        "Fell and hit head on the slide; nurse checked her",  # description
        True,                                                 # Tier 2? yes
        True,                                                 # step 1 done? yes
        "called mom and told the principal",                  # update
        True, False,                                          # step 2 yes, step 3 no
        "done 3", "done 4",
        tmp_path=tmp_path,
    )
    rec = state.record
    assert rec.tier is Tier.SIGNIFICANT and rec.closed
    assert rec.steps[StepId.NURSE_EVALUATES].source is Source.LLM_CONFIRMED
    assert rec.steps[StepId.INFORM_ADMIN].source is Source.USER  # rejected suggestion, set manually
    # the second reading only asked about steps still pending
    steps_asked = [s for t, s in llm.step_calls if t == "called mom and told the principal"]
    assert steps_asked and StepId.NURSE_EVALUATES not in steps_asked
    assert (tmp_path / "incident-20261015-100000.md").exists()


def test_skipped_step_resurfaces(tmp_path):
    llm = FakeInterpreter(Tier.MINOR, {
        "small scrape on knee, logged it in the nurse log": ProgressReport(steps_done=(StepId.RECORD_NURSE_LOG,)),
    })
    state, console = play(
        llm,
        "small scrape on knee, logged it in the nurse log",
        True,           # Tier 3
        True,           # step 2 done
        "quit", True,   # quit with open steps
        tmp_path=tmp_path,
    )
    assert statuses(state)[:2] == [StepStatus.PENDING, StepStatus.DONE]
    assert "Step 1 was skipped" in console.text
    assert "Step 1: Give first aid." in console.text


def test_rejected_tier_user_chooses_and_tier1_shows_911_now(tmp_path):
    llm = FakeInterpreter(Tier.SIGNIFICANT, agree=2)
    state, console = play(
        llm,
        "student not breathing well after bee sting",
        False, "1",       # reject Tier 2, choose Tier 1
        "quit", True,
        tmp_path=tmp_path,
    )
    assert state.record.tier is Tier.EMERGENCY
    assert "wasn't able to make a determination of severity" in console.text
    assert "NOW: Call 911 right away" in console.text


def test_rejected_agreed_tier_user_chooses(tmp_path):
    llm = FakeInterpreter(Tier.SIGNIFICANT)  # all 3 readings agree
    state, console = play(
        llm,
        "small scrape on elbow, back in class",
        False, "3",       # reject Tier 2, choose Tier 3
        "quit", True,
        tmp_path=tmp_path,
    )
    tier_events = [e.detail for e in state.record.timeline if e.kind is EventKind.TIER]
    assert state.record.tier is Tier.MINOR
    assert tier_events == [f"{Tier.MINOR.label} ({Source.USER})"]  # recorded as the user's choice
    assert "3/3 readings agree" in console.text
    assert "wasn't able to make a determination of severity" not in console.text
    assert any(isinstance(p, AskChoice) and p.question == "Which tier?" for p in console.prompts)


def test_escalate_starts_new_checklist_and_rereads_narrative(tmp_path):
    llm = FakeInterpreter(Tier.MINOR, {
        # tier 1 re-reading of the whole narrative (tier 3 readings find nothing)
        "nosebleed\nit won't stop and he passed out, 911 called": ProgressReport(steps_done=(StepId.CALL_911,)),
    })
    state, console = play(
        llm,
        "nosebleed",
        True,
        "it won't stop and he passed out, 911 called",
        "escalate", "1",
        True,                                               # 911 called? yes
        "quit", True,
        tmp_path=tmp_path,
    )
    rec = state.record
    assert rec.tier is Tier.EMERGENCY and rec.previous_tiers == [Tier.MINOR]
    assert rec.steps[StepId.CALL_911].status is StepStatus.DONE
    reread_text, _ = llm.step_calls[-1]
    assert "nosebleed" in reread_text and (reread_text, StepId.CALL_911) in llm.step_calls


def test_bad_command_argument(tmp_path):
    state, console = play(FakeInterpreter(Tier.MINOR), "scrape", True, "done x", "quit", True, tmp_path=tmp_path)
    assert "Usage: done <step number 1-3>" in console.text


@pytest.mark.parametrize("trials_agree", [1, 3])
def test_llm_failure_falls_back_to_manual(tmp_path, trials_agree):
    class Broken(FakeInterpreter):
        def classify_tier(self, description):
            raise TimeoutError("model offline")

    state, console = play(Broken(None, agree=trials_agree), "scrape", "3", "quit", True, tmp_path=tmp_path)
    assert state.record.tier is Tier.MINOR
    assert state.record.steps and "model offline" in console.text
