import csv
from collections.abc import Iterable, Iterator


def parse_csv_rows(lines: Iterable[str]) -> Iterator[dict[str, str]]:
    """Потоковий парсер рядків CSV у словники без повної матеріалізації."""
    reader = csv.DictReader(lines)
    yield from reader