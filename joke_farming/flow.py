from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .client import generate_options, join_context
from .structures import STRUCTURES


@dataclass
class Step:
    name: str
    description: str
    prompt_builder: Callable[[str, str, str], str]
    option_count: int = 3
    temperature: float = 0.8


BASE_SYSTEM = """You are a joke-writing assistant. You follow a step-by-step process:
1) Clarify the absurdity.
2) State the point plainly.
3) Choose a humorous premise.
4) Apply a structure.
5) Find a twist by thinking oppositely.
6) Set the tone.
7) Polish wording for brevity and specificity.
Return only the requested output for the current step.
"""


def _clarify_point(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Absurdity seed: {absurdity}",
            f"Voice: {voice}",
            "Task: State the point plainly in one sentence.",
            "Return a JSON array of 3 short options.",
        ]
    )


def _choose_premise(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Absurdity seed: {absurdity}",
            f"Plain point: {prior}",
            f"Voice: {voice}",
            "Task: Propose a humorous premise that leads the audience to the point.",
            "Return a JSON array of 3 options.",
        ]
    )


def _choose_structure(absurdity: str, voice: str, prior: str) -> str:
    structures = "\n".join(
        f"- {item['name']}: {item['summary']}" for item in STRUCTURES
    )
    return join_context(
        [
            f"Absurdity seed: {absurdity}",
            f"Premise: {prior}",
            f"Voice: {voice}",
            "Available structures:",
            structures,
            "Task: Suggest 3 structure choices from the list that best fit.",
            "Return a JSON array of the structure names only.",
        ]
    )


def _draft_joke(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Absurdity seed: {absurdity}",
            f"Structure: {prior}",
            f"Voice: {voice}",
            "Task: Write a first-draft joke using the structure.",
            "Return a JSON array of 3 draft jokes.",
        ]
    )


def _find_twist(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Draft joke: {prior}",
            f"Voice: {voice}",
            "Task: Think oppositely and propose a twist that adds another layer.",
            "Return a JSON array of 3 revised jokes with twists.",
        ]
    )


def _tune_tone(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Joke draft: {prior}",
            f"Voice: {voice}",
            "Task: Adjust the emotional attitude to cue the audience properly.",
            "Return a JSON array of 3 tone variants.",
        ]
    )


def _polish(absurdity: str, voice: str, prior: str) -> str:
    return join_context(
        [
            f"Joke draft: {prior}",
            f"Voice: {voice}",
            "Task: Polish for brevity, clarity, and specificity.",
            "Return a JSON array of 3 polished options.",
        ]
    )


STEPS = [
    Step(
        name="Point",
        description="State the absurdity in plain language.",
        prompt_builder=_clarify_point,
    ),
    Step(
        name="Premise",
        description="Choose a humorous premise.",
        prompt_builder=_choose_premise,
    ),
    Step(
        name="Structure",
        description="Pick a structure from suggestions.",
        prompt_builder=_choose_structure,
        temperature=0.4,
    ),
    Step(
        name="Draft",
        description="Create a first draft with the chosen structure.",
        prompt_builder=_draft_joke,
    ),
    Step(
        name="Twist",
        description="Find an oppositional twist.",
        prompt_builder=_find_twist,
    ),
    Step(
        name="Tone",
        description="Tune the emotional attitude.",
        prompt_builder=_tune_tone,
    ),
    Step(
        name="Polish",
        description="Polish for brevity and specificity.",
        prompt_builder=_polish,
        temperature=0.6,
    ),
]


def generate_step_options(
    *,
    model: str,
    voice: str,
    absurdity: str,
    prior: str,
    step: Step,
) -> list[str]:
    prompt = step.prompt_builder(absurdity, voice, prior)
    return generate_options(
        model=model,
        system_prompt=BASE_SYSTEM,
        user_prompt=prompt,
        count=step.option_count,
        temperature=step.temperature,
    )
