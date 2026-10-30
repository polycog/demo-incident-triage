# Student injury triage assistant

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)
[![Built with cognition](https://img.shields.io/badge/cognition-inside-7b2fbe?labelColor=f3effa&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjIgMCAzNiAzNiIgZmlsbD0ibm9uZSI+PHBvbHlnb24gcG9pbnRzPSIyMCw0IDM0LjMsMTQuNCAyOC44LDMxLjYgMTEuMiwzMS42IDUuNywxNC40IiBzdHJva2U9IiM3YjJmYmUiIHN0cm9rZS13aWR0aD0iMi4yIi8+PGcgc3Ryb2tlPSIjYzQ3ZDIwIiBzdHJva2Utd2lkdGg9IjIiPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjAiIHkyPSI0Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSIzNC4zIiB5Mj0iMTQuNCIvPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjguOCIgeTI9IjMxLjYiLz48bGluZSB4MT0iMjAiIHkxPSIyMCIgeDI9IjExLjIiIHkyPSIzMS42Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSI1LjciIHkyPSIxNC40Ii8+PC9nPjxnIGZpbGw9IiM3YjJmYmUiPjxjaXJjbGUgY3g9IjIwIiBjeT0iNCIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iMzQuMyIgY3k9IjE0LjQiIHI9IjMuMiIvPjxjaXJjbGUgY3g9IjI4LjgiIGN5PSIzMS42IiByPSIzLjIiLz48Y2lyY2xlIGN4PSIxMS4yIiBjeT0iMzEuNiIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iNS43IiBjeT0iMTQuNCIgcj0iMy4yIi8+PC9nPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjQuNiIgZmlsbD0iI2M0N2QyMCIvPjwvc3ZnPgo=)](https://github.com/polycog/cognition)
[![cognition on PyPI](https://img.shields.io/pypi/v/polycog-cognition?label=cognition%20on%20PyPI&color=c47d20&labelColor=f3effa&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjIgMCAzNiAzNiIgZmlsbD0ibm9uZSI+PHBvbHlnb24gcG9pbnRzPSIyMCw0IDM0LjMsMTQuNCAyOC44LDMxLjYgMTEuMiwzMS42IDUuNywxNC40IiBzdHJva2U9IiM3YjJmYmUiIHN0cm9rZS13aWR0aD0iMi4yIi8+PGcgc3Ryb2tlPSIjYzQ3ZDIwIiBzdHJva2Utd2lkdGg9IjIiPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjAiIHkyPSI0Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSIzNC4zIiB5Mj0iMTQuNCIvPjxsaW5lIHgxPSIyMCIgeTE9IjIwIiB4Mj0iMjguOCIgeTI9IjMxLjYiLz48bGluZSB4MT0iMjAiIHkxPSIyMCIgeDI9IjExLjIiIHkyPSIzMS42Ii8+PGxpbmUgeDE9IjIwIiB5MT0iMjAiIHgyPSI1LjciIHkyPSIxNC40Ii8+PC9nPjxnIGZpbGw9IiM3YjJmYmUiPjxjaXJjbGUgY3g9IjIwIiBjeT0iNCIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iMzQuMyIgY3k9IjE0LjQiIHI9IjMuMiIvPjxjaXJjbGUgY3g9IjI4LjgiIGN5PSIzMS42IiByPSIzLjIiLz48Y2lyY2xlIGN4PSIxMS4yIiBjeT0iMzEuNiIgcj0iMy4yIi8+PGNpcmNsZSBjeD0iNS43IiBjeT0iMTQuNCIgcj0iMy4yIi8+PC9nPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjQuNiIgZmlsbD0iI2M0N2QyMCIvPjwvc3ZnPgo=)](https://pypi.org/project/polycog-cognition/)

## 1. Summary

A **neurosymbolic** agent, built with the [`cognition`](https://github.com/polycog/cognition) library, that helps preschool and childcare staff follow a child injury policy in real time. Staff describe an incident as it happens, and the agent determines the triage tier, gives the required next step, and tracks progress through the policy's checklist and deadlines. It only tracks the policy: it never contacts anyone or files anything, it never makes independent judgments.

### Contents

1. [Summary](#1-summary)
2. [Problem Statement](#2-problem-statement)
3. [Technical Approach and Demo](#3-technical-approach-and-demo)
4. [Install, Run, and Test](#4-install-run-and-test)
5. [License and Disclaimers](#5-license-and-disclaimers)

---

## 2. Problem Statement

When a child is hurt, preschool and childcare staff must triage the injury, take the right steps in the right order, and meet strict licensing deadlines, often while keeping supervision ratios and with the record kept on paper forms and binders. Missed notifications or late reports lead to licensing deficiencies and lost trust with families. Keeping track of these procedural and licensing requirements places a heavy cognitive burden on center directors, whose expertise is better spent supporting staff, improving classroom environments, and mentoring teachers. An LLM can understand a teacher's hurried, in-the-moment description of what happened, but it can't be trusted to apply the policy, keep the deadlines, or give the same answer twice, and a hallucinated tier or a skipped step could compromise a child's safety. A **neurosymbolic** approach combines both: the LLM listens to staff, and [symbolic decision process](https://docs.polycog.ai/ideas/kadp.html) follows the policy step by step, with staff confirming every suggestion.

See [the full problem statement and opportunity](docs/usecase.md).

---

## 3. Technical Approach and Demo
The agent follows the policy to the letter while letting staff speak naturally. An LLM only interprets what staff type, turning it into the policy's own terms: a suggested tier, or a yes/no on whether one named step is done. Each suggestion is put to staff as a yes/no question, and only their answers change the incident record. The policy itself is encoded as data, and a **[symbolic decision process](https://docs.polycog.ai/ideas/kadp.html)**, made of WHEN/THEN operators written with `cognition` and ranked by priority, decides everything else: which steps to check, the checklist and deadlines, and the earliest unfinished step to do next. With no LLM in these decisions, the same state always leads to the same action, and staff can still pick the tier and mark steps themselves if the LLM is unavailable. See [the technical approach](docs/approach.md) for details.

**Demo:** [watch the triage assistant guide staff through a student injury](https://drive.google.com/file/d/1LSy0GMOcpanyjX-ScRHjvEYihpc7BRKN/view?usp=drive_link)

---

## 4. Install, Run, and Test

### 4.1 Clone the repository

```bash
git clone https://github.com/polycog/demo-incident-triage.git
cd demo-incident-triage
```

### 4.2 Install the dependencies

`cognition` requires **Python 3.13 or later**. The project is managed with [uv](https://docs.astral.sh/uv/), which creates the environment and installs everything in [`pyproject.toml`](pyproject.toml):

```bash
uv sync
```

This installs:

- **`polycog-cognition`**, the `cognition` library, published on PyPI under that name;
- **`pydantic-ai-slim[openai]`**, which `cognition` builds on, with the OpenAI extra for the language model;
- **`rich`**, for the terminal console.

### 4.3 Choose a language model

All settings are in [`config.toml`](config.toml). Choose a profile by setting `use` under `[llm]`:

| Profile | Model | Needs |
|---|---|---|
| `openai` (default) | `gpt-4o` | `OPENAI_API_KEY` |
| `local` | `openai/gpt-oss-20b` | An OpenAI-compatible server at `http://localhost:1234/v1` (such as LM Studio) |

For the `openai` profile, export your key in the shell you run the assistant from, and keep it out of the repository:

```bash
export OPENAI_API_KEY="sk-..."
```

To add your own profile, add a `[llm.profiles.<name>]` table. With `base_url` set, `model` is sent to that OpenAI-compatible server, and `api_key_env` names the environment variable holding its key. Without `base_url`, `model` is any [pydantic-ai](https://ai.pydantic.dev/) model id.

`[policy]` fills in the `[bracketed]` values in the policy text, such as the district office name, reporting deadlines, and when the school day ends.

### 4.4 Run the assistant

```bash
uv run python -m injury_triage            # add --trace to see which operator runs each cycle
```

Describe what happened, e.g. "Fell and hit her head on the slide; the nurse checked her". Confirm the suggested tier, then report progress in your own words. Instead of an update, you can type a command:

| Command | Effect |
|---|---|
| `status` | Show the checklist and deadlines |
| `done <n>` / `undo <n>` | Mark step *n* done or not done |
| `escalate` | The situation got worse: move up a tier and start its checklist |
| `help` | List the commands |
| `quit` | End the session and save the log |

When the session ends, a draft incident log is saved to `reports/` as `.md` and `.json`. Pressing Ctrl-C exits without saving.

### 4.5 Run the tests

The test suite uses [pytest](https://docs.pytest.org/) and runs fully offline: it replaces the LLM with a fake and staff with a scripted console, so it needs no API key and makes no paid calls.

```bash
uv run --group dev pytest
```

---

## 5. License and Disclaimers

This project is released under the [Apache License 2.0](LICENSE). Copyright © 2026 Polycog, Inc. If you use it, please cite it using the metadata in [`CITATION.cff`](CITATION.cff).

> **Disclaimer:** this project is a technical demonstration of neurosymbolic reasoning. It is not a medical or safety tool, and the built-in policy is an example not endorsed by any childcare provider, licensing agency or health authority. Do not rely on it in a real emergency: call your local emergency number and follow your organization's actual procedures.
