import csv
from pathlib import Path
from typing import Dict, List, Tuple
import random

from .models import Joke
from .config import get_settings


class JokeDataStore:
    """
    Holds jokes in memory and provides methods to get random jokes and categories.
    """

    def __init__(self) -> None:
        self._all_jokes: List[Joke] = []
        self._jokes_by_category: Dict[str, List[Joke]] = {}
        self._categories: List[str] = []

    def load_from_file(self) -> None:
        settings = get_settings()
        data_dir = settings.DATA_DIR

        # Determine whether to use CSV or TSV
        csv_path = data_dir / settings.JOKES_CSV_FILENAME
        tsv_path = data_dir / settings.JOKES_TSV_FILENAME

        if csv_path.is_file():
            file_path = csv_path
            delimiter = ","
        elif tsv_path.is_file():
            file_path = tsv_path
            delimiter = "\t"
        else:
            raise FileNotFoundError(
                f"No jokes file found. Expected {csv_path} or {tsv_path}."
            )

        self._load_file(file_path, delimiter)

    def _load_file(self, file_path: Path, delimiter: str) -> None:
        self._all_jokes.clear()
        self._jokes_by_category.clear()
        self._categories.clear()

        with file_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            required_fields = {"id", "joke", "category"}
            if not required_fields.issubset(reader.fieldnames or []):
                raise ValueError(
                    f"Jokes file {file_path} is missing required columns: {required_fields}"
                )

            for row in reader:
                joke_id = int(row["id"])
                joke_text = str(row["joke"]).strip()
                category = str(row["category"]).strip()

                if not joke_id or not joke_text or not category:
                    # Skip malformed rows
                    continue

                joke = Joke(id=joke_id, joke=joke_text, category=category)
                self._all_jokes.append(joke)

                if category not in self._jokes_by_category:
                    self._jokes_by_category[category] = []
                self._jokes_by_category[category].append(joke)

        self._categories = sorted(self._jokes_by_category.keys())

        if not self._all_jokes:
            raise ValueError(f"No valid jokes loaded from {file_path}")

    def get_random_joke(self) -> Joke:
        if not self._all_jokes:
            raise RuntimeError("Jokes data not loaded or empty.")
        return random.choice(self._all_jokes)

    def get_random_joke_by_category(self, category: str) -> Tuple[bool, Joke | None]:
        """
        Returns (found, joke).
        found=False if category does not exist or has no jokes.
        """
        jokes = self._jokes_by_category.get(category)
        if not jokes:
            return False, None
        return True, random.choice(jokes)

    def get_categories(self) -> List[str]:
        return list(self._categories)

    def get_category_count(self) -> int:
        return len(self._categories)
