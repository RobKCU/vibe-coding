from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .client import DEFAULT_MODEL
from .flow import STEPS, generate_step_options
from .session import StepRecord, new_session


def _prompt_text(label: str, *, allow_empty: bool = False) -> str:
    while True:
        value = input(label).strip()
        if value or allow_empty:
            return value
        print("Please enter a value.")


def _render_options(options: list[str]) -> None:
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")


def _choose_option(options: list[str]) -> str | None:
    prompt = "Choose [1-{n}], r=regen, e=edit, v=voice, b=back, q=quit (default 1): ".format(
        n=len(options)
    )
    choice = input(prompt).strip().lower()
    if not choice:
        return options[0]
    if choice in {"r", "e", "v", "b", "q"}:
        return choice
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    print("Invalid choice.")
    return None


def _default_session_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("sessions") / f"joke-session-{stamp}.json"


def run() -> None:
    parser = argparse.ArgumentParser(description="Interactive joke farming CLI")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use")
    parser.add_argument("--session-out", default=None, help="Path to save session JSON")
    parser.add_argument("--no-save", action="store_true", help="Do not save session")
    args = parser.parse_args()

    print("Joke Farming Wizard")
    print("--------------------")
    absurdity = _prompt_text("Absurdity seed (what's funny about it?): ")
    voice = _prompt_text("Voice/persona (e.g., dry, jaded, bright): ")

    session = new_session(model=args.model, voice=voice, absurdity=absurdity)

    prior = ""
    step_index = 0
    while step_index < len(STEPS):
        step = STEPS[step_index]
        regen_count = 0
        while True:
            print("\nStep: {name}".format(name=step.name))
            print(step.description)
            prompt = step.prompt_builder(absurdity, session.voice, prior)
            options = generate_step_options(
                model=args.model,
                voice=session.voice,
                absurdity=absurdity,
                prior=prior,
                step=step,
            )
            if not options:
                print("No options received; trying again.")
                regen_count += 1
                continue
            _render_options(options)

            choice = _choose_option(options)
            if choice is None:
                continue
            if choice == "r":
                regen_count += 1
                continue
            if choice == "v":
                session.voice = _prompt_text("Adjust voice (leave empty to keep): ", allow_empty=True) or session.voice
                regen_count += 1
                continue
            if choice == "b":
                if step_index == 0 or not session.steps:
                    print("Already at the first step.")
                    continue
                session.steps.pop()
                step_index -= 1
                prior = session.steps[-1].choice if session.steps else ""
                break
            if choice == "q":
                print("Exiting early. Session will be saved if enabled.")
                if not args.no_save:
                    out_path = Path(args.session_out) if args.session_out else _default_session_path()
                    session.save(out_path)
                    print(f"Session saved to {out_path}")
                return
            if choice == "e":
                edited = _prompt_text("Enter your version: ")
                selection = edited
                options = [selection]
            else:
                selection = choice

            session.steps.append(
                StepRecord(
                    name=step.name,
                    prompt=prompt,
                    options=options,
                    choice=selection,
                    regen_count=regen_count,
                )
            )
            prior = selection
            step_index += 1
            break

    session.final_joke = prior
    print("\nFinal Joke")
    print("----------")
    print(session.final_joke or "")

    if not args.no_save:
        out_path = Path(args.session_out) if args.session_out else _default_session_path()
        session.save(out_path)
        print(f"\nSession saved to {out_path}")
