from collections.abc import Iterable, Iterator
from .models import BookRecord



def normalize_book_titles(books: Iterable[BookRecord]) -> Iterator[BookRecord]:
    """Ледача трансформація: приведення назв та авторів до єдиного регістру."""
    for book in books:
        yield book._replace(
            title=book.title.strip().title(),
            author=book.author.strip().title(),
        )