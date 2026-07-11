"""An intermediate-level Python file for testing concept extraction."""

from collections import defaultdict, Counter
import os
from pathlib import Path


def process_data(items: list) -> dict:
    result = defaultdict(list)
    for i, item in enumerate(items):
        category = item.get("category", "unknown")
        result[category].append(item)
    return dict(result)


def read_file_safe(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except PermissionError:
        return []


def analyze_text(text):
    words = text.lower().split()
    word_counts = Counter(words)
    return word_counts.most_common(5)


def transform_data(values):
    squared = [x * x for x in values if x > 0]
    even_squares = {x: x * x for x in values if x % 2 == 0}
    return squared, even_squares


def pair_lists(a, b):
    return list(zip(a, b))


class DataProcessor:
    def __init__(self, name):
        self.name = name
        self._data = []

    @property
    def count(self):
        return len(self._data)

    def add(self, item):
        self._data.append(item)

    def __len__(self):
        return len(self._data)


def main():
    path = Path("data")
    if path.exists():
        files = list(path.glob("*.csv"))
        for file in files:
            data = read_file_safe(str(file))
            print(f"{file.name}: {len(data)} lines")


if __name__ == "__main__":
    main()
