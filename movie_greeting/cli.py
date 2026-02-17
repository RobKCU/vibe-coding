from .client import create_greeting
from .genres import choose_genre


def run() -> None:
    genre = choose_genre()
    try:
        greeting = create_greeting(genre)
    except RuntimeError as exc:
        print(exc)
        return
    print(greeting)
