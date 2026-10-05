import sys
from pathlib import Path

# Автоматично додаємо папку src до шляхів пошуку модулів
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Далі йдуть ваші звичайні імпорти:
import time
import tracemalloc
from itertools import chain, islice, pairwise
from stream_processor.analytics import (
    calculate_streaming_book_stats,
    find_first_book,
)
from stream_processor.batches import batched_books
from stream_processor.generator_data import generate_books_dataset
from stream_processor.models import BookPageRangeIterator, BookRecord
from stream_processor.pipeline import build_book_pipeline


# --- Етап жадібної обробки (Eager) для порівняльного експерименту ---
def eager_read_and_process(path: Path, min_year: int) -> list[BookRecord]:
    """Жадібна реалізація: завантажує весь файл у пам'ять списком."""
    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    records: list[BookRecord] = []
    for line in lines[1:]:
        parts = line.strip().split(",")
        if len(parts) != 5:
            continue
        try:
            year = int(parts[3])
            pages = int(parts[4])
            if 1450 <= year <= 2026 and pages > 0:
                if year >= min_year:
                    records.append(
                        BookRecord(
                            isbn=parts[0],
                            title=parts[1].title(),
                            author=parts[2].title(),
                            year=year,
                            pages=pages,
                        )
                    )
        except ValueError:
            continue
    return records


def measure_execution(func, *args) -> tuple[any, float, float]:
    """Вимірює час виконання (сек) та пікове споживання оперативної пам'яті (МБ)."""
    tracemalloc.start()
    start_time = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start_time
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / (1024 * 1024)


def main() -> None:
    data_path = Path("data/books.csv")

    print("[1] Генерація датасету (500 000 записів)...")
    generate_books_dataset(data_path, count=500_000)

    # 1. Отримання перших N книг після заданого року через itertools.islice
    print("\n[2] Перші 5 книг, виданих після 2015 року (через itertools.islice):")
    pipeline_islice = build_book_pipeline(data_path, min_year=2015)
    first_five = list(islice(pipeline_islice, 5))
    for book in first_five:
        print(f"  - {book.title} ({book.author}, {book.year}) — {book.pages} стор.")

    # 2. Generator Expression: підрахунок суми сторінок
    print("\n[3] Generator Expression (обчислення суми сторінок перших 50 книг):")
    pipeline_gen_expr = build_book_pipeline(data_path, min_year=2000)
    top_50 = islice(pipeline_gen_expr, 50)
    pages_gen_expr = (b.pages for b in top_50)  # Генераторний вираз
    print(f"  Сума сторінок: {sum(pages_gen_expr)}")

    # 3. Batch processing (пакетна обробка)
    print("\n[4] Пакетна обробка (batches по 3 записи):")
    pipeline_batch = build_book_pipeline(data_path, min_year=2020)
    for i, batch in enumerate(islice(batched_books(pipeline_batch, 3), 2), start=1):
        print(f"  Пакет #{i} ({len(batch)} записи): {[b.title for b in batch]}")

    # 4. Потокова агрегація та пошук книги з максимальною кількістю сторінок
    print("\n[5] Потокова статистика (one-pass aggregation):")
    pipeline_stats = build_book_pipeline(data_path)
    stats = calculate_streaming_book_stats(pipeline_stats)
    print(f"  Валідних записів оброблено: {stats['count']}")
    print(f"  Середня кількість сторінок: {stats['average_pages']:.2f}")
    if stats["max_pages_book"]:
        mb = stats["max_pages_book"]
        print(f"  Книга з макс. к-стю сторінок: '{mb.title}' ({mb.pages} стор.)")

    # 5. itertools.pairwise (аналіз сусідніх елементів)
    print("\n[6] itertools.pairwise (динаміка зміни обсягу між сусідніми книгами):")
    for prev_book, curr_book in pairwise(first_five):
        diff = curr_book.pages - prev_book.pages
        print(f"  '{curr_book.title}' проти '{prev_book.title}': {diff:+d} стор.")

    # 6. itertools.chain (об'єднання двох незалежних джерел)
    print("\n[7] itertools.chain (об'єднання двох конвеєрів):")
    stream_author_1 = build_book_pipeline(data_path, target_author="George Orwell")
    stream_author_2 = build_book_pipeline(data_path, target_author="Ivan Franko")
    combined_stream = chain(islice(stream_author_1, 2), islice(stream_author_2, 2))
    for book in combined_stream:
        print(f"  З об'єднаного потоку: {book.title} — {book.author}")

    # 7. Демонстрація власного класу-ітератора
    print("\n[8] Власний клас-ітератор BookPageRangeIterator:")
    custom_iterator = BookPageRangeIterator(first_five[:3])
    for item in custom_iterator:
        print(f"  Власний ітератор повернув: {item.title}")

    # 8. Lazy Search з Early Termination
    print("\n[9] Early Termination (пошук першої книги автора Agatha Christie):")
    pipeline_search = build_book_pipeline(data_path)
    found = find_first_book(pipeline_search, lambda b: b.author == "Agatha Christie")
    if found:
        print(f"  Знайдено: {found.title} (Рік: {found.year}, ISBN: {found.isbn})")

    # 9. Експериментальна частина: Порівняння Eager vs Lazy на 100 000 записах
    print("\n[10] Бенчмарк: Eager vs Lazy (100 000 рядків, фільтр year >= 2000):")

    # Жадібне завантаження
    _, eager_time, eager_mem = measure_execution(
        eager_read_and_process, data_path, 2000
    )

    # Ліниве завантаження (споживання потоку)
    def consume_lazy(path: Path, min_year: int) -> int:
        p = build_book_pipeline(path, min_year=min_year)
        total = 0
        for _ in p:
            total += 1
        return total

    _, lazy_time, lazy_mem = measure_execution(consume_lazy, data_path, 2000)

    print(f"  {'Підхід':<10} | {'Час (сек)':<12} | {'Пікова пам памʼять (МБ)':<22}")
    print(f"  {'-'*10}-|-{'-'*12}-|-{'-'*22}")
    print(f"  {'Eager':<10} | {eager_time:<12.4f} | {eager_mem:<22.4f}")
    print(f"  {'Lazy':<10} | {lazy_time:<12.4f} | {lazy_mem:<22.4f}")


if __name__ == "__main__":
    main()