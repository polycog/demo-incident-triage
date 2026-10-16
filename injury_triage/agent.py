"""
Assembling the cognitive agent (Cogent):

* sensor   ``now``     -> io.i.now     (wall clock, read each turn)
* actuator ``console`` -> io.o.console (all user interaction)
* decision process     -> the operators and generators in ``operators.py``,
                          ranked by ``Priority``

``CheckStep`` gets its LLM interpreter here, built once and shared by
every operator the generator creates. ``run`` loops one turn at a time
until the incident is closed.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, cast

from cognition import (
    Actuator,
    Cogent,
    DecisionProcess,
    NamedObject,
    OPERATOR_SELF_PARAM,
    create_sensor,
    sorting_evaluator,
)

from .operators import (
    AdviseNextStep,
    CheckStep,
    ChooseTier,
    CloseIncident,
    ConfirmAgreedTier,
    ConfirmDisputedTier,
    ConfirmStepDone,
    EndSession,
    EscalateTier,
    GatherDescription,
    ProposeTier,
    ReadProgress,
    SetStepByNumber,
    ShowStatus,
)
from .language import LLMStepInterpreter
from .state import TriageState

type TriageAgent = Cogent[DecisionProcess[TriageState]]

def by_priority(action: Any, _state: TriageState, _io: Any) -> tuple[int, int]:
    """Ranking key: each operator's (priority, tiebreak)"""

    return cast(NamedObject, action).params[OPERATOR_SELF_PARAM].sort_key()


def build_agent(
    console: Actuator[Any, Any],
    clock: Callable[[], datetime] = lambda: datetime.now().astimezone(),
) -> TriageAgent:
    """Wire state, operators, ranking, sensor, and actuator together"""

    state = TriageState()
    dp = DecisionProcess(state)  # same state object survives each per-turn reinit

    operators = (
        # intake & tier
        GatherDescription(),
        ProposeTier(),
        ConfirmAgreedTier(),
        ConfirmDisputedTier(),
        ChooseTier(),
        # progress
        ReadProgress(),
        # commands
        ShowStatus(),
        SetStepByNumber(),
        EscalateTier(),
        EndSession(),
        # end of turn
        CloseIncident(),
        AdviseNextStep(),
    )
    for op in operators:
        dp.add_operator(op)
    # one operator per item to check / proposal to confirm
    dp.add_generator(CheckStep, LLMStepInterpreter())
    dp.add_generator(ConfirmStepDone, None)
    dp.add_action_evaluator(sorting_evaluator(by_priority, name="policy_priority"))

    agent: TriageAgent = Cogent(dp, name="injury_triage")
    agent.add_sensor(create_sensor("now", clock))
    agent.add_actuator(console)
    return agent


def run(agent: TriageAgent) -> TriageState:
    """One cogent loop per user turn, until the incident is closed"""

    agent(lambda c: not c.dp.state.record.closed)
    return agent.dp.state
