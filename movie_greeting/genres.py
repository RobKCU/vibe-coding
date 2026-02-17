GENRES = [
    "noir detective",
    "romantic comedy",
    "science fiction",
    "western",
]


def choose_genre() -> str:
    print("Choose a film genre for your greeting:")
    for index, genre in enumerate(GENRES, start=1):
        print(f"{index}. {genre}")

    while True:
        choice = input("Enter a number or genre name: ").strip()
        if choice.isdigit():
            selected = int(choice)
            if 1 <= selected <= len(GENRES):
                return GENRES[selected - 1]
        lowered_choice = choice.casefold()
        for genre in GENRES:
            if lowered_choice == genre.casefold():
                return genre
        print("Please enter a valid option number or genre name.")
