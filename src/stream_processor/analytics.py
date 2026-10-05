from collections.abc import Callable, Iterable
from .models import BookRecord


def calculate_streaming_book_stats(books: Iterable[BookRecord]) -> dict:
    """Обчислює статистику за один прохід конвеєра без вивантаження у список."""
    count = 0
    total_pages = 0
    max_book: BookRecord | None = None
    min_pages: int | None = None

    for book in books:
        count += 1
        total_pages += book.pages

        if max_book is None or book.pages > max_book.pages:
            max_book = book

        if min_pages is None or book.pages < min_pages:
            min_pages = book.pages

    return {
        "count": count,
        "total_pages": total_pages,
        "average_pages": (total_pages / count) if count else 0.0,
        "min_pages": min_pages,
        "max_pages_book": max_book,
    }


def find_first_book(
    books: Iterable[BookRecord],
    predicate: Callable[[BookRecord], bool],
) -> BookRecord | None:
    """Лінивий пошук першої відповідної книги з Early Termination."""
    for book in books:
        if predicate(book):
            return book
    return None