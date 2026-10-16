# Student injury triage assistant

A small interactive CLI that helps K-12 staff follow a student injury
policy in the moment. You describe what happened; it tells you the tier
and the next step, and keeps track as you report progress. It does not
contact anyone or file anything. It only tracks the policy.

Built with [`polycog-cognition`](https://github.com/polycog/cognition) to show
a neurosymbolic design: the LLM only *interprets* text, and a declarative
decision process (plus a human yes/no) decides what happens.

## What the agent does

The agent is **neurosymbolic**: a neural part (the LLM) turns free text into structured guesses,
and a symbolic part (the policy as data, plus rule-based operators) decides what happens. They meet
at a narrow interface: the LLM can only answer in the policy's own terms, i.e. a `Tier` or a
yes/no about one named step, and its answers are proposals until you confirm them.

A session goes like this:

1. **Describe what happened** *(you)*, in your own words, including anything already done.
2. **Classify the injury** *(neural)*. The LLM maps your description onto a `Tier`, several times;
   agreement between the classifications becomes the confidence you see. You confirm its suggestion
   or pick the tier yourself. **Red** = Tier 1, **yellow** = Tier 2, **green** = Tier 3.
3. **Check progress** *(neural, scoped symbolically)*. For the description and every later update,
   the symbolic side picks which steps the LLM should check (only those still pending). The LLM then
   evaluates, one step at a time, whether the step was reported done or not, using the step's
   definition from the policy.
4. **Confirm with you** *(human)*. Each LLM suggestion is put to you as a yes/no question.
   Only your answers change the record.
5. **Track and guide** *(symbolic)*. The checklist, deadlines and the **earliest unfinished step**
   come from the encoded policy and the confirmed record, with no LLM involved, so a skipped step
   comes back. Steps 3–5 repeat with each update until every step is done or you quit.

Instead of an update you can type a command: `status`, `done <n>`, `undo <n>`, `escalate`, `help`,
`quit`. When the session ends, a draft log is saved to `reports/` (`.md` and `.json`).

**Who decides what happens next is always deterministic.** The agent is a set of independent WHEN/THEN
operators, not a scripted flow and not an LLM planner. Each cycle, every operator whose WHEN holds
is a candidate, and the most urgent one (lowest `Priority` value) runs. Finishing an LLM check comes
first, then your confirmations, then typed commands, then reading new text, then closing the session
once everything is done, and finally showing the next step. The same state always leads to the same
action, and if the LLM is unavailable the agent still works: you pick the tier and mark steps yourself.

## The built-in policy

The agent ships with one triage policy, encoded as data in [`policy.py`](injury_triage/policy.py).
Each tier has criteria (which the LLM uses to classify a description) and an ordered checklist.
Values in *italics* are the `[bracketed]` placeholders, set under `[policy]` in `config.toml`.

**Tier 1: Emergency** (red): life-threatening or possibly so: unresponsive, trouble breathing,
severe bleeding, suspected neck or spine injury, seizure, severe allergic reaction, obvious major fracture.

| # | Step | Due |
|---|---|---|
| 1 | Call 911 right away. Don't wait for an administrator. | right away |
| 2 | Start first aid, CPR/AED, or emergency meds per protocol. | right away |
| 3 | Notify nurse and administrator. | right away |
| 4 | Administrator calls parent immediately. | right away |
| 5 | Notify *district office* within *1 hour*. | *1 hour* after the incident is entered |
| 6 | Report filed within *24 hours*. | *24 hours* after the incident is entered |

**Tier 2: Significant** (yellow): needs evaluation or outside care: any head injury, possible
fracture or sprain, wound that may need stitches, eye or dental injury, student can't return to class.

| # | Step | Due |
|---|---|---|
| 1 | Nurse evaluates the student. | |
| 2 | Call parent before student returns to class or leaves. | before the student returns to class or leaves |
| 3 | Inform administrator same day. | end of today |
| 4 | Report filed by *end of next school day*. | next weekday at *15:30* |

**Tier 3: Minor** (green): first aid only: small scrape, minor bruise, nosebleed that stops,
student returns to class.

| # | Step | Due |
|---|---|---|
| 1 | Give first aid. | |
| 2 | Record in nurse visit log. | |
| 3 | Notify parent same day by *note / call / app*. | end of today |

If unsure between two tiers, the policy says to choose the higher one, and `escalate` moves an
incident up a tier if things get worse.

## Run

```bash
uv sync
uv run python -m injury_triage            # add --trace to see each decision-process choice
uv run --group dev pytest                 # offline tests (fake LLM, scripted console)
```

Settings, including the LLM and the policy's `[bracketed]` placeholders, are in
[`config.toml`](config.toml). The LLM is chosen from named profiles there:
`openai` (default) uses `gpt-4o` (needs `OPENAI_API_KEY`), and `local` uses
`openai/gpt-oss-20b` served by LM Studio at `http://localhost:1234/v1`.
Switch by setting `use` under `[llm]`.

## How it's built

| File | Role |
|---|---|
| [`policy.py`](injury_triage/policy.py) | The policy as data: `Tier`, `StepId`, `Deadline`, `PolicyStep`, `POLICY`. Docstrings feed the LLM prompts. |
| [`record.py`](injury_triage/record.py) | `IncidentRecord`: only **confirmed** facts, with a timeline. |
| [`state.py`](injury_triage/state.py) | Decision-process state: the record plus pending LLM proposals and commands. |
| [`language.py`](injury_triage/language.py) | The only LLM use: `EnumClassifier` (tier) and `ModelPopulator` (progress, one call per pending step). |
| [`operators.py`](injury_triage/operators.py) | The decision process: independent WHEN/THEN operators, ranked by `Priority`. |
| [`agent.py`](injury_triage/agent.py) | The `Cogent`: `now` clock sensor, `console` actuator, operators, ranking. |

The guarantees come from the structure:

- **LLM output is only a proposal.** `ProposeTier` and `CheckStep` store suggestions; `ConfirmAgreedTier`, `ConfirmDisputedTier`,
  and `ConfirmStepDone` write to the record only after a human yes.
- **No re-classification.** Progress readings only ask about steps that are still pending.
  Confirmed facts are never sent back to the LLM.
- **Deterministic control.** When several operators apply, `sorting_evaluator` picks by `Priority`,
  so the same state always leads to the same next action.

`escalate` covers a situation that gets worse (a nosebleed that won't stop, a head injury
where the student becomes unresponsive). It moves to a higher tier only, starts that tier's checklist,
and re-reads the narrative so steps already done can be confirmed again.
