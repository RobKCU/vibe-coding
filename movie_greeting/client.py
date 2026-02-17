import os
from pathlib import Path

from openai import OpenAI


def _load_api_key() -> str | None:
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


def create_greeting(genre: str) -> str:
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Set it in your shell or add OPENAI_API_KEY=... to .env."
        )

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-5.2",
        input=f"Give me a one-sentence {genre} greeting.",
    )
    return response.output_text
