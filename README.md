# Student injury triage assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)
[![Built with cognition](https://img.shields.io/badge/built%20with-cognition-7b2fbe?labelColor=f3effa&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjIgMCAzNiAzNiIgZmlsbD0ibm9uZSI+PHBvbHlnb24gcG9pbnRzPSIyMCw0IDM0LjMsMTQuNCAyOC44LDMxLjYgMTEuMiwzMS42IDUuNywxNC40IiBzdHJva2U9IiM3YjJmYmUiIHN0cm9rZS13aWR0aD0iMi4yIi8+PGcgc3Ryb2tlPSIjYzQ3ZDIwIiBzdHJva2Utd2lkdGg9IjIiPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjAiIHkyPSI0Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSIzNC4zIiB5Mj0iMTQuNCIvPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjguOCIgeTI9IjMxLjYiLz48bGluZSB4MT0iMjAiIHkxPSIyMCIgeDI9IjExLjIiIHkyPSIzMS42Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSI1LjciIHkyPSIxNC40Ii8+PC9nPjxnIGZpbGw9IiM3YjJmYmUiPjxjaXJjbGUgY3g9IjIwIiBjeT0iNCIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iMzQuMyIgY3k9IjE0LjQiIHI9IjMuMiIvPjxjaXJjbGUgY3g9IjI4LjgiIGN5PSIzMS42IiByPSIzLjIiLz48Y2lyY2xlIGN4PSIxMS4yIiBjeT0iMzEuNiIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iNS43IiBjeT0iMTQuNCIgcj0iMy4yIi8+PC9nPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjQuNiIgZmlsbD0iI2M0N2QyMCIvPjwvc3ZnPgo=)](https://github.com/polycog/cognition)
[![cognition on PyPI](https://img.shields.io/pypi/v/polycog-cognition?label=cognition%20on%20PyPI&color=c47d20&labelColor=f3effa&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjIgMCAzNiAzNiIgZmlsbD0ibm9uZSI+PHBvbHlnb24gcG9pbnRzPSIyMCw0IDM0LjMsMTQuNCAyOC44LDMxLjYgMTEuMiwzMS42IDUuNywxNC40IiBzdHJva2U9IiM3YjJmYmUiIHN0cm9rZS13aWR0aD0iMi4yIi8+PGcgc3Ryb2tlPSIjYzQ3ZDIwIiBzdHJva2Utd2lkdGg9IjIiPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjAiIHkyPSI0Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSIzNC4zIiB5Mj0iMTQuNCIvPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjguOCIgeTI9IjMxLjYiLz48bGluZSB4MT0iMjAiIHkxPSIyMCIgeDI9IjExLjIiIHkyPSIzMS42Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSI1LjciIHkyPSIxNC40Ii8+PC9nPjxnIGZpbGw9IiM3YjJmYmUiPjxjaXJjbGUgY3g9IjIwIiBjeT0iNCIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iMzQuMyIgY3k9IjE0LjQiIHI9IjMuMiIvPjxjaXJjbGUgY3g9IjI4LjgiIGN5PSIzMS42IiByPSIzLjIiLz48Y2lyY2xlIGN4PSIxMS4yIiBjeT0iMzEuNiIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iNS43IiBjeT0iMTQuNCIgcj0iMy4yIi8+PC9nPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjQuNiIgZmlsbD0iI2M0N2QyMCIvPjwvc3ZnPgo=)](https://pypi.org/project/polycog-cognition/)

**A neurosymbolic agent: the LLM interprets, and the symbolic system decides.**

A reference demo for [`polycog-cognition`](https://github.com/polycog/cognition): an interactive
CLI that helps K-12 staff follow a student injury policy in the moment. Staff describe what
happened, and it gives them the tier and the next step, then tracks progress as they report it.
It only tracks the policy. It never contacts anyone or files anything.

**Demo:** [watch the triage assistant guide staff through a student injury](https://drive.google.com/file/d/1LSy0GMOcpanyjX-ScRHjvEYihpc7BRKN/view?usp=drive_link)

- **Neural:** the LLM turns free text into the policy's own terms (a `Tier`, or a yes/no about
  one named step). Its answers are only proposals.
- **Symbolic:** the policy is encoded as data, and WHEN/THEN operators enforce it at run time.
  They decide everything else: which steps the LLM checks, the checklist and deadlines, and the
  earliest unfinished step to do next.

Highlights:

- **Human confirmation:** each LLM proposal is put to staff as a yes/no question, and only their
  answers change the record.
- **Deterministic control:** ranked operators, not a scripted flow or an LLM planner, so the
  same state always leads to the same action.
- **Works without the LLM:** staff can pick the tier and mark steps themselves.
- **Policy as data:** tiers, criteria, checklists and deadlines live in one Python file.
- **Any OpenAI-compatible model,** hosted or local.

## Contents

- [Quick start](#quick-start)
- [Configuration](#configuration)
- [The built-in policy](#the-built-in-policy)
- [Adapting the policy](#adapting-the-policy)
- [Project layout](#project-layout)
- [Development](#development)
- [Privacy](#privacy)
- [License](#license)

## Quick start

> [!WARNING]
> **This is a demonstration, not a medical or safety tool.** The built-in policy is an example
> and is not endorsed by any school, district or health authority. Do not rely on this software
> in a real emergency: call your local emergency number and follow your organization's actual
> procedures. See the [license](LICENSE) for the full warranty disclaimer.

**Requirements:** Python 3.13+, [uv](https://docs.astral.sh/uv/), and either an OpenAI API key
or a local OpenAI-compatible server.

```bash
git clone https://github.com/polycog/demo-incident-triage.git
cd demo-incident-triage
uv sync

export OPENAI_API_KEY=sk-...              # for the default "openai" profile
uv run python -m injury_triage            # add --trace to see each decision-process choice
```

Instead of typing an update, you can type a command:

| Command | Effect |
|---|---|
| `status` | Show the checklist and deadlines |
| `done <n>` / `undo <n>` | Mark step *n* done or not done |
| `escalate` | Move the incident up a tier |
| `help` | List the commands |
| `quit` | End the session and save the log |

When the session ends, a draft log is saved to `reports/` as `.md` and `.json`. Pressing
Ctrl-C exits without saving.

`escalate` covers a situation that gets worse, such as a nosebleed that won't stop or a head
injury where the student becomes unresponsive. It only moves up a tier and starts that tier's
checklist. It also re-reads what you've written so far, so you can confirm again any steps
already done.

## Configuration

All settings are in [`config.toml`](config.toml).

**Language model.** Choose a profile by setting `use` under `[llm]`:

| Profile | Model | Needs |
|---|---|---|
| `openai` (default) | `gpt-4o` | `OPENAI_API_KEY` |
| `local` | `openai/gpt-oss-20b` | An OpenAI-compatible server at `http://localhost:1234/v1` (such as LM Studio) |

To add your own profile, add a `[llm.profiles.<name>]` table. With `base_url` set, `model` is
sent to that OpenAI-compatible server, and `api_key_env` names the environment variable holding
its key. Without `base_url`, `model` is any [pydantic-ai](https://ai.pydantic.dev/) model id.

**Policy placeholders.** The `[policy]` table fills in the `[bracketed]` values in the policy
text, such as the district office name, reporting deadlines, and when the school day ends.

## The built-in policy

The example policy is encoded as data in [`policy.py`](injury_triage/policy.py). Each tier has
criteria, which the LLM uses to classify a description, and an ordered checklist. Values in
*italics* are the `[bracketed]` placeholders set under `[policy]` in `config.toml`.

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

If unsure between two tiers, the policy says to choose the higher one.

## Adapting the policy

To try a different policy, edit [`policy.py`](injury_triage/policy.py):

- `Tier` holds the tiers and their criteria. The docstrings are part of the LLM prompt, so write
  them as clear definitions.
- `StepId` and `PolicyStep` describe each checklist step, and the step's description is what the
  LLM uses to decide whether it was reported done.
- `Deadline` and `POLICY` link steps to tiers and set when each one is due.

Simple values such as names and deadlines can be changed in `config.toml` without touching code.
Run the tests after changing the policy.

## Project layout

| File | Role |
|---|---|
| [`policy.py`](injury_triage/policy.py) | The policy as data: `Tier`, `StepId`, `Deadline`, `PolicyStep`, `POLICY`. Docstrings feed the LLM prompts. |
| [`record.py`](injury_triage/record.py) | `IncidentRecord`: only **confirmed** facts, with a timeline. |
| [`state.py`](injury_triage/state.py) | Decision-process state: the record plus pending LLM proposals and commands. |
| [`language.py`](injury_triage/language.py) | The only LLM use: `EnumClassifier` (tier) and `ModelPopulator` (progress, one call per pending step). |
| [`operators.py`](injury_triage/operators.py) | The decision process: independent WHEN/THEN operators, ranked by `Priority`. |
| [`agent.py`](injury_triage/agent.py) | The `Cogent`: `now` clock sensor, `console` actuator, operators, ranking. |
| [`console.py`](injury_triage/console.py) | Terminal I/O and rendering (checklist, next-step panel). |
| [`reports.py`](injury_triage/reports.py) | Writes the end-of-session draft log. |
| [`config.py`](injury_triage/config.py) | Loads `config.toml`. |

How the guarantees map to the code:

- **Proposals vs. record.** `ProposeTier` and `CheckStep` only store suggestions.
  `ConfirmAgreedTier`, `ConfirmDisputedTier` and `ConfirmStepDone` write to the record after a
  human yes. The tier is classified several times, and how often the answers agree is the
  confidence you see.
- **No re-classification.** Progress checks only ask about pending steps, and confirmed facts
  are never sent back to the LLM.
- **Operator order.** Each cycle, `sorting_evaluator` runs the applicable operator with the
  lowest `Priority`: finish an LLM check, then your confirmations, then typed commands, then
  read new text, then close the session once everything is done, and finally show the next step.

## Development

```bash
uv sync
uv run --group dev pytest       # offline: uses a fake LLM and a scripted console, no API key needed
```

## Privacy

Session logs in `reports/` may contain details about students. That folder is listed in
`.gitignore`, so keep it out of version control and handle it according to your organization's
data policies. Descriptions you type are sent to whichever LLM you configure. Use the `local`
profile if text must stay on your machine.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Polycog Inc.
