"""
Run the injury triage assistant:  python -m injury_triage [--trace]

``--trace`` prints, each decision cycle, which operators applied and
which one was chosen. All settings come from ``config.toml``.
"""

from __future__ import annotations

import argparse

from rich.panel import Panel

from .agent import build_agent, run
from .console import RichConsole, Say
from .language import load_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Student injury triage assistant")
    parser.add_argument("--trace", action="store_true", help="show each decision-process choice")
    args = parser.parse_args()

    console = RichConsole()

    console.actuate(Say(Panel(
        "Student injury triage assistant\n"
        "[dim]Tracks the injury policy and tells you the next step. "
        "It does not contact anyone or file anything.[/]\n"
        f"[dim]Language model: {load_model().model_name}[/]",
        border_style="cyan",
    )))

    agent = build_agent(console)
    if args.trace:
        _enable_trace(agent, console)

    try:
        run(agent)
    except (KeyboardInterrupt, EOFError):
        console.actuate(Say("\n[yellow]Interrupted -- session not saved.[/]"))


def _enable_trace(agent, console: RichConsole) -> None:
    """Print which operators were proposed and which one was chosen, each cycle"""

    import logging

    class _Trace(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            msg = record.getMessage()
            if "apply phase started" in msg:
                dp = agent.dp
                proposed = ", ".join(str(a).split("[")[0] for a in dp._potential_actions)  # noqa: SLF001
                console.out.print(f"[dim magenta]  ⟳ proposed: {proposed}  →  chose: {dp.chosen_action}[/]")

    log = logging.getLogger("cognition.decision.core")
    log.setLevel(logging.INFO)
    log.addHandler(_Trace())


if __name__ == "__main__":
    main()
