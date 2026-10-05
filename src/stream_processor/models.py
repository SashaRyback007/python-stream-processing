from collections.abc import Iterator
from typing import NamedTuple


class BookRecord(NamedTuple):
    """Незмінне представлення запису книги."""
    isbn: str
    title: str
    author: str
    year: int
    pages: int


class BookPageRangeIterator:
    """Власний клас-ітератор для обходу колекції книг за протоколом __iter__ та __next__."""

    def __init__(self, books: list[BookRecord]) -> None:
        self._books = books
        self._index = 0

    def __iter__(self) -> Iterator[BookRecord]:
        return self

    def __next__(self) -> BookRecord:
        if self._index >= len(self._books):
            raise StopIteration
        book = self._books[self._index]
        self._index += 1
        return book