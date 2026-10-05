from collections.abc import Iterable, Iterator
from stream_processor.models import BookRecord
from .models import BookRecord


def validate_books(rows: Iterable[dict[str, str]]) -> Iterator[BookRecord]:
    """Валідує поля запису, відсіює пошкоджені рядки та створює BookRecord."""
    for row in rows:
        try:
            isbn = row["isbn"].strip()
            title = row["title"].strip()
            author = row["author"].strip()
            year = int(row["year"])
            pages = int(row["pages"])
        except (ValueError, KeyError, TypeError):
            continue

        if not isbn or not title or not author:
            continue
        if not (1450 <= year <= 2026):
            continue
        if pages <= 0 or pages > 10000:
            continue

        yield BookRecord(
            isbn=isbn,
            title=title,
            author=author,
            year=year,
            pages=pages,
        )


def filter_by_author_and_year(
    books: Iterable[BookRecord],
    target_author: str | None = None,
    min_year: int | None = None,
) -> Iterator[BookRecord]:
    """Фільтрує потік книг за автором та мінімальним роком видання."""
    for book in books:
        if target_author and book.author.lower() != target_author.lower():
            continue
        if min_year is not None and book.year < min_year:
            continue
        yield book