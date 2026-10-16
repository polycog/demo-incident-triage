"""
Language understanding: the ONLY place an LLM is used.

* ``LLMTierInterpreter`` classifies a description into a ``Tier``
  (several trials; agreement becomes the confidence).
* ``LLMStepInterpreter`` evaluates whether ONE policy step was reported
  done, using that step's definition from the policy.

Answers are always in the policy's own terms (a ``Tier``, or yes/no for
a ``StepId``) and are only proposals: the LLM never changes state or
decides what happens next -- operators do that, after a human confirms.
The model comes from the ``[llm]`` profile in config.toml (``load_model``).
"""

from __future__ import annotations

import os

from cognition import EnumClassifier, ModelPopulator
from pydantic import BaseModel, Field
from pydantic_ai.models import Model, infer_model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import load_config
from .policy import PolicyStep, Tier
from .state import TierProposal

# ===


def load_model() -> Model:
    """
    The model for the config.toml ``[llm]`` profile named by ``use``:
    an OpenAI-compatible server if it sets ``base_url``, else a pydantic-ai model id
    """

    llm = load_config()["llm"]
    profile = llm["profiles"][llm["use"]]
    if base_url := profile.get("base_url"):
        api_key = os.environ.get(profile.get("api_key_env", ""), "not-needed")
        return OpenAIChatModel(profile["model"], provider=OpenAIProvider(base_url=base_url, api_key=api_key))
    return infer_model(profile["model"])


class LLMTierInterpreter:
    """Suggests a tier from free text"""

    num_trials = 3
    """tier votes per classification (agreement = confidence)"""

    timeout_secs = 60
    """per LLM call"""

    classifier = EnumClassifier(
        Tier,
        task_desc=(
            "A K-12 school staff member is describing a student injury. "
            "Choose the policy tier. If it could plausibly be either of two "
            "tiers, choose the more severe one."
        ),
    )

    def __init__(self) -> None:
        self.llm = load_model()

    def classify_tier(self, description: str) -> TierProposal:
        tier, agreement = self.classifier(
            description, self.llm, num_trials=self.num_trials, timeout_secs=self.timeout_secs
        )
        return TierProposal(tier, agreement)


class StepCheck(BaseModel):
    """Whether the text reports that the policy step has been done"""

    done: bool = Field(
        description="true only if the text says the step has actually been done (not just planned or requested)"
    )


class LLMStepInterpreter:
    """Tests one policy step: does the text say it has been done?"""

    timeout_secs = 60
    """per LLM call"""

    checker = ModelPopulator(
        StepCheck,
        task_desc=(
            "A school staff member is responding to a student injury and "
            "reporting what has happened. Check the ONE policy step given "
            "under Extra Information."
        ),
    )

    def __init__(self) -> None:
        self.llm = load_model()

    def step_done(self, text: str, tier: Tier, step: PolicyStep) -> bool:
        check = self.checker(
            text, self.llm, f"This is a {tier.label} injury.", f"Policy step: {step.id.__doc__}",
            timeout_secs=self.timeout_secs,
        )
        return check.done
