import csv
import random
from pathlib import Path

AUTHORS = [
    "Taras Shevchenko",
    "Ivan Franko",
    "Lesya Ukrainka",
    "George Orwell",
    "Agatha Christie",
    "J.R.R. Tolkien",
    "Stephen King",
    "Isaac Asimov",
]

TITLES_PART1 = [
    "Chronicles", "Journey", "Shadow", "Echo",
    "Empire", "Dawn", "Silence", "Code"
]
TITLES_PART2 = [
    "Time", "Stars", "the Wind", "Darkness",
    "Future", "the Mind", "Eternity"
]


def generate_books_dataset(path: Path, count: int = 100_000) -> None:
    """Генерує файл CSV заданого обсягу з тестовими та некоректними записами."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["isbn", "title", "author", "year", "pages"])

        for i in range(1, count + 1):
            # Періодично генеруємо биті рядки для тестування фільтрів валідації
            if i % 200 == 0:
                writer.writerow(
                    [f"ERR-{i}", "Corrupted Entry", "", "invalid_year", -20]
                )
                continue

            isbn = f"978-0-{random.randint(100, 999)}-{random.randint(10000, 99999)}-{i % 10}"
            title = f"{random.choice(TITLES_PART1)} of {random.choice(TITLES_PART2)} Vol. {i}"
            author = random.choice(AUTHORS)
            year = random.randint(1920, 2024)
            pages = random.randint(60, 1400)

            writer.writerow([isbn, title, author, year, pages])