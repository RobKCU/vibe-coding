import json
import os
from pathlib import Path
from typing import Iterable

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.2"


def load_api_key() -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    env_file = Path(".env")
    if not env_file.is_file():
        return None

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() != "OPENAI_API_KEY":
            continue
        api_key = value.strip().strip("\"'")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            return api_key

    return None


def _coerce_options(text: str, expected: int) -> list[str]:
    text = text.strip()
    if not text:
        return []

    try:
        data = json.loads(text)
        if isinstance(data, list):
            options = [str(item).strip() for item in data if str(item).strip()]
            return options[:expected]
    except json.JSONDecodeError:
        pass

    options: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line[0].isdigit() and ("." in line[:3] or ")" in line[:3]):
            _, _, remainder = line.partition(" ")
            line = remainder.strip() or line.lstrip("0123456789.). ")
        if line.startswith("-"):
            line = line.lstrip("- ")
        if line:
            options.append(line)
    return options[:expected]


def generate_options(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    count: int,
    temperature: float,
) -> list[str]:
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Set it in your shell or add OPENAI_API_KEY=... to .env."
        )

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )

    options = _coerce_options(response.output_text, count)
    if len(options) < count:
        fallback = response.output_text.strip()
        if fallback and fallback not in options:
            options.append(fallback)
    return options


def join_context(lines: Iterable[str]) -> str:
    return "\n".join(line for line in lines if line.strip())
