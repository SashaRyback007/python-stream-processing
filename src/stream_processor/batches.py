from collections.abc import Iterable, Iterator
from itertools import islice
from .models import BookRecord


def batched_books(
    books: Iterable[BookRecord], batch_size: int
) -> Iterator[list[BookRecord]]:
    """Розбиває потік записів на пачки фіксованого розміру за допомогою islice."""
    iterator = iter(books)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch