from collections.abc import Iterator
from pathlib import Path

from stream_processor.filters import filter_by_author_and_year, validate_books
from stream_processor.models import BookRecord
from stream_processor.parsers import parse_csv_rows
from stream_processor.readers import read_lines
from stream_processor.transformations import normalize_book_titles


def build_book_pipeline(
    path: Path,
    target_author: str | None = None,
    min_year: int | None = None,
) -> Iterator[BookRecord]:
    """Створює ледачий конвеєр: read -> parse -> validate -> transform -> filter."""
    lines = read_lines(path)
    rows = parse_csv_rows(lines)
    valid = validate_books(rows)
    normalized = normalize_book_titles(valid)
    filtered = filter_by_author_and_year(
        normalized,
        target_author=target_author,
        min_year=min_year,
    )
    return filtered