"""
Console I/O as a cognition Actuator, plus display helpers.

Operators never print or read directly; they send a request to the
``console`` actuator (``io.o.console(...)``) and get the answer back.
That keeps the decision process testable with a scripted console.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cognition import Actuator
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from .policy import Deadline, PolicySettings, PolicyStep, Tier
from .record import IncidentRecord, StepStatus

# === requests the console actuator understands


@dataclass(frozen=True)
class Say:
    """Show something"""

    content: RenderableType


@dataclass(frozen=True)
class AskText:
    """Ask for a line of free text"""

    prompt: str


@dataclass(frozen=True)
class AskYesNo:
    """Ask a yes/no question"""

    question: str
    default: bool | None = None


@dataclass(frozen=True)
class AskChoice:
    """Ask the user to pick one key from ``choices`` (key -> label)"""

    question: str
    choices: dict[str, str]
    default: str | None = None


@dataclass(frozen=True)
class TypedText:
    """Reply to :class:`AskText`: what was typed, and when it was entered"""

    text: str
    at: datetime


type ConsoleRequest = Say | AskText | AskYesNo | AskChoice
type ConsoleReply = TypedText | str | bool | None


class RichConsole(Actuator[ConsoleRequest, ConsoleReply]):
    """Terminal console"""

    def __init__(self) -> None:
        self.out = Console()

    @property
    def name(self) -> str:
        return "console"

    def actuate(self, param: ConsoleRequest) -> ConsoleReply:
        match param:
            case Say(content=c):
                self.out.print(c)
                return None
            case AskText(prompt=p):
                text = Prompt.ask(f"[bold cyan]{p}[/]", console=self.out).strip()
                return TypedText(text, datetime.now().astimezone())
            case AskYesNo(question=q, default=d):
                # no default unless given: the user must type y or n
                return Confirm.ask(f"[bold]{q}[/]", default=... if d is None else d, console=self.out)  # type: ignore[arg-type]
            case AskChoice(question=q, choices=ch, default=d):
                for k, label in ch.items():
                    self.out.print(f"  [bold]{k}[/]  {label}")
                return Prompt.ask(f"[bold]{q}[/]", choices=list(ch), default=d, console=self.out)


# === display helpers


def tier_badge(tier: Tier) -> Text:
    """Colored tier label: red / yellow / green"""

    return Text(f" {tier.label.upper()} ", style=f"bold black on {tier.color}")


def _due_text(step: PolicyStep, record: IncidentRecord, policy: PolicySettings, now: datetime) -> Text:
    if step.deadline is None or record.started_at is None:
        return Text("")
    if step.deadline is Deadline.IMMEDIATELY:
        pending = record.status(step) is StepStatus.PENDING
        return Text("right away", style=f"bold {record.tier.color}" if pending else "dim")  # type: ignore[union-attr]

    due = step.deadline.due(record.started_at, policy)
    if due is None:  # event-based ("before the student leaves"): the wording says it
        return Text("")

    when = due.strftime("%-I:%M %p") if due.date() == now.date() else due.strftime("%a %b %-d, %-I:%M %p")
    if record.status(step) is StepStatus.PENDING and now > due:
        return Text(f"OVERDUE (was {when})", style="bold red")
    return Text(f"by {when}", style="dim")


_STATUS_MARK = {
    StepStatus.DONE: Text("✔ done", style="green"),
    StepStatus.PENDING: Text("○ to do", style="bold"),
}


def checklist(record: IncidentRecord, policy: PolicySettings, now: datetime) -> RenderableType:
    """The tier's steps with status and deadlines"""

    assert record.tier is not None
    table = Table(box=None, pad_edge=False, show_header=False)
    table.add_column(justify="right")
    table.add_column()
    table.add_column()
    table.add_column()

    nxt = record.next_step()
    for step in record.protocol_steps:
        style = "bold" if step is nxt else ("dim" if record.status(step) is not StepStatus.PENDING else "")
        text = Text(step.text(policy), style=style)
        table.add_row(f"{step.number}.", _STATUS_MARK[record.status(step)], text, _due_text(step, record, policy, now))

    return Panel(table, title=tier_badge(record.tier), title_align="left", border_style=record.tier.color)


def next_step_panel(record: IncidentRecord, policy: PolicySettings, now: datetime) -> RenderableType:
    """What to do next, with a warning about skipped steps"""

    assert record.tier is not None
    step = record.next_step()
    if step is None:
        return Text("All steps are complete.", style="bold green")

    parts: list[RenderableType] = []
    skipped = record.skipped()
    if skipped:
        nums = [str(s.number) for s in skipped]
        which = f"Step {nums[0]} was" if len(nums) == 1 else f"Steps {', '.join(nums[:-1])} and {nums[-1]} were"
        parts.append(Text(f"⚠ {which} skipped -- go back.", style="bold yellow"))

    line = Text(f"Step {step.number}: ", style="bold")
    line.append(step.text(policy), style=f"bold {record.tier.color}")
    due = _due_text(step, record, policy, now)
    if due:
        line.append("  ")
        line.append(due)
    parts.append(line)

    return Panel(Group(*parts), title="NEXT", title_align="left", border_style=record.tier.color)
