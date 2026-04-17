#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_FILES = ["jokes.csv", "jokes.tsv"]


def validate_row(row, filename, errors):
    """
    Validate a single CSV/TSV row with fields:
      id,joke,category

    Rules:
      - id: must be an integer
      - joke: must start with:
          "Yo mama is", "Yo mama's ", or "Yo mama was"
        AND if it starts with "Yo mama's ", the next word must not be "so".
      - category: non-empty
    """
    row_id = row.get("id")
    joke = row.get("joke")
    category = row.get("category")

    # Use "unknown" if id is missing so output is still usable
    display_id = str(row_id).strip() if row_id is not None else "unknown"

    # id, joke, category must be present
    if row_id is None or joke is None or category is None:
        errors.append(
            f"{filename}: id={display_id}: missing one of required fields: id,joke,category"
        )
        return

    # id must be an integer
    try:
        int(row_id)
    except ValueError:
        errors.append(
            f"{filename}: id={display_id}: id '{row_id}' is not a valid integer"
        )

    # joke must start with allowed prefixes
    joke_stripped = str(joke).strip()
    allowed_prefix = (
        joke_stripped.startswith("Yo mama is")
        or joke_stripped.startswith("Yo mama's ")
        or joke_stripped.startswith("Yo mama was")
    )
    if not allowed_prefix:
        errors.append(
            f"{filename}: id={display_id}: joke does not start with one of "
            f"'Yo mama is', 'Yo mama's ', or 'Yo mama was': {joke_stripped!r}"
        )
    else:
        # Additional rule: if it starts with "Yo mama's ", the next word must not be "so"
        if joke_stripped.startswith("Yo mama's "):
            # After "Yo mama's " (length 11), check the next word
            rest = joke_stripped[len("Yo mama's ") :]
            # Get the first word of the remainder
            first_word = rest.split(None, 1)[0] if rest else ""
            if first_word.lower() == "so":
                errors.append(
                    f"{filename}: id={display_id}: 'Yo mama' jokes must not use the 'Yo mama's so ...' pattern: "
                    f"{joke_stripped!r}"
                )

    # category must be non-empty
    category_stripped = str(category).strip()
    if not category_stripped:
        errors.append(f"{filename}: id={display_id}: category is empty")


def lint_file(path: Path) -> list[str]:
    errors: list[str] = []

    # Detect delimiter from extension
    if path.suffix.lower() == ".csv":
        delimiter = ","
    elif path.suffix.lower() == ".tsv":
        delimiter = "\t"
    else:
        return [
            f"{path.relative_to(ROOT)}: unsupported file extension (expected .csv or .tsv)"
        ]

    rel_name = str(path.relative_to(ROOT))

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        required_fields = {"id", "joke", "category"}
        if not required_fields.issubset(reader.fieldnames or []):
            errors.append(
                f"{rel_name}: missing required columns; expected at least {sorted(required_fields)}"
            )
            return errors

        for row in reader:
            validate_row(row, rel_name, errors)

    return errors


def main():
    files: list[Path] = []

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            files.append(Path(arg))
    else:
        # Default: look for jokes.csv and jokes.tsv under ./data
        for name in DEFAULT_FILES:
            p = DATA_DIR / name
            if p.is_file():
                files.append(p)

    if not files:
        print(
            "No joke files found to lint. Looked for jokes.csv/tsv in ./data by default."
        )
        sys.exit(0)

    all_errors: list[str] = []
    for p in files:
        errs = lint_file(p)
        all_errors.extend(errs)

    if all_errors:
        print("Jokes linting found issues:")
        for e in all_errors:
            print("  -", e)
        sys.exit(1)

    print("Jokes linting passed with no issues.")
    sys.exit(0)


if __name__ == "__main__":
    main()
