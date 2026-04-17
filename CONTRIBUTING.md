# Contributing to Yo Mama Jokes API

Contributions are welcome! This document explains how to set up a dev environment, what tooling is used, and the specific rules for adding jokes.

---

## Overview

When contributing, you should:

- Work in a feature branch and open a Pull Request.
- Run the core Python checks (`black`, `pytest`, jokes linter).
- Optionally run the JS/CSS/HTML/Markdown linters (also run in CI as informational checks).
- Follow the CSV/TSV schema and joke style rules when adding/editing jokes.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages when possible.

---

## 1. Getting Started

### 1.1 Fork and Clone

1. Fork the repo on GitHub.
2. Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/yomama-api.git
   cd yomama-api
   ```

3. Add the original repo as `upstream`:

   ```bash
   git remote add upstream https://github.com/azstrait/yomama-api.git
   ```

### 1.2 Python Dev Environment (Required)

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   # python -m venv .venv
   # .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Install dev tools (if not already in requirements):

   ```bash
   pip install black pytest
   ```

4. Run tests:

   ```bash
   pytest
   ```

5. Lint Python:

   ```bash
   black .
   ```

### 1.3 JS/CSS/HTML/Markdown Linting (Optional but Recommended)

JavaScript, CSS, HTML, and Markdown linting use `npm` tooling:

1. Install Node.js (if you don’t already have it).
2. Install dev dependencies:

   ```bash
   npm install
   ```

3. Lint JavaScript:

   ```bash
   npm run lint:js
   ```

4. Lint CSS:

   ```bash
   npm run lint:css
   ```

5. Lint Markdown:

   ```bash
   npm run lint:md
   ```

6. Lint HTML:

   ```bash
   npm run lint:html
   ```

These are optional for contributors but are run in CI as *informational* checks (they won’t fail the build, but fixing issues they report is appreciated).

---

## 2. Jokes Linting (CSV/TSV)

There is a small Python script to validate jokes files (`jokes.csv` / `jokes.tsv`) for basic consistency and formatting rules.

To run it:

```bash
python scripts/lint_jokes.py
```

By default, it looks for `data/jokes.csv` and `data/jokes.tsv`. You can also target a specific file:

```bash
python scripts/lint_jokes.py data/my_jokes.csv
```

It checks:

- `id` is an integer.
- `joke` starts with **one** of:
  - `Yo mama is`
  - `Yo mama was`
  - `Yo mama's <noun>`  
    (but **not** `Yo mama's so …` – that pattern is rejected)
- `category` is non-empty.
- Required columns (`id`, `joke`, `category`) are present.

**If you add or edit jokes, please run this linter and fix any reported issues.**

---

## 3. CI Notes

The CI pipelines (for PRs, pushes, and publish workflows) run:

**Required (must pass):**

- `black --check .`
- `pytest`
- `python scripts/lint_jokes.py`

**Informational (non-fatal):**

- `npm run lint:js`
- `npm run lint:css`
- `npm run lint:md`
- `npm run lint:html`

If the npm-based linters fail, CI will log the issues but **will not** block your PR. However, you’re encouraged to fix any warnings/errors they report.

---

## 4. Making Changes

1. Create a feature branch:

   ```bash
   git checkout -b feature/my-cool-thing
   ```

2. Make your changes:
   - Update code (API, frontend, etc.).
   - Update jokes (if applicable).
   - Add or adjust tests under `tests/`.

3. Run core checks:

   ```bash
   black .
   pytest
   python scripts/lint_jokes.py
   ```

4. Optionally run the JS/CSS/MD/HTML linters:

   ```bash
   npm run lint:js
   npm run lint:css
   npm run lint:md
   npm run lint:html
   ```

5. Commit using [**Conventional Commits**](https://www.conventionalcommits.org/) style, for example:

   - `feat(categories): add category filter to API`
   - `fix: handle empty jokes file`
   - `chore: update dependencies`
   - `docs(docker): document Docker usage`

6. Push and open a Pull Request:

   ```bash
   git push origin feature/my-cool-thing
   ```

   Then open a PR against `azstrait/yomama-api:main`.

In your PR description, please include:

- What you changed.
- Why you changed it.
- Any relevant notes for reviewers.

CI will automatically run the checks described above on your PR.

---

## 5. Adding or Editing Jokes

Jokes live in a CSV/TSV file with columns:

```csv
id,joke,category
```

### 5.1 Schema Rules

1. `id`:
   - Must be an **unquoted integer**.
   - Must be unique.

2. `joke`:
   - Must be enclosed in **double quotes**.
   - Must begin with one of:
     - `Yo mama is`
     - `Yo mama was`
     - `Yo mama's <noun>` (e.g. `Yo mama's feet are ...`)  
       **Note:** `Yo mama's so ...` is rejected by the linter.
   - Any internal commas are fine as long as the field is quoted.

3. `category`:
   - Must be enclosed in **double quotes**.
   - Should be a lowercase, single-word category where possible (e.g. `old`, `fat`, `ugly`, `nerd`).

### 5.2 Example

```csv
1,"Yo mama is so old, her first car was a chariot.","old"
2,"Yo mama is so fat, when she sits around the house, she sits AROUND the house.","fat"
3,"Yo mama's teeth are so yellow, when she smiles, traffic slows down.","ugly"
```

### 5.3 Guidelines

- Aim for jokes that are in the spirit of classic “Yo Mama” jokes.
- Avoid hate speech, slurs, or anything targeting real individuals or protected groups.
- Categories should be descriptive but not derogatory whenever possible.
- Always run:

  ```bash
  python scripts/lint_jokes.py
  ```

  after editing jokes.

---

## 6. Style & Code Guidelines

- **Python**
  - Use `black` for formatting.
  - Keep code consistent with existing style (FastAPI patterns, Pydantic models, etc.).

- **JavaScript**
  - Keep code consistent with the existing `app/static/js/app.js`.
  - Use ESLint’s recommendations as a guide, but minor stylistic differences are generally fine.

- **HTML**
  - Keep templates readable and minimal.
  - Avoid inline JS where possible (use `app/static/js/app.js`).

- **General**
  - Favor small, focused changes per PR.
  - If you’re making significant changes to behavior or configuration, please also update:
    - `README.md`
    - Any relevant tests.

---

## 7. Questions

If you’re unsure about anything (joke formatting, code structure, tests), feel free to:

- Open a draft PR and ask in the PR description.
- Or open an issue with your question and context.

Thanks for contributing to **Yo Mama Jokes API**!