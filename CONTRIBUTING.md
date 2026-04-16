# Contributing to Yo Mama Jokes API

Contributions are welcome! This document outlines how to get set up for development, what’s expected in contributions, and specific rules for adding jokes.

---

## Getting Started

### 1. Fork and Clone

1. Fork the repo on GitHub.
2. Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/yomama-api.git
   cd yomama-api
   ```

3. Add the original repo as upstream:

   ```bash
   git remote add upstream https://github.com/azstrait/yomama-api.git
   ```

### 2. Set Up Dev Environment

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

3. Install dev tools (if not in requirements):

   ```bash
   pip install black pytest
   ```

4. Run tests:

   ```bash
   pytest
   ```

5. Lint:

   ```bash
   black .
   ```

---

## Making Changes

1. Create a feature branch:

   ```bash
   git checkout -b feature/my-cool-thing
   ```

2. Make your changes:
   - Update code (API, frontend, etc.).
   - Add or adjust tests under `tests/`.
   - Run `pytest` and `black .` locally before committing.

3. Commit using **conventional commit** style, e.g.:

   - `feat: add category filter to API`
   - `fix: handle empty jokes file`
   - `chore: update dependencies`
   - `docs: document Docker usage`

4. Push and open a Pull Request:

   ```bash
   git push origin feature/my-cool-thing
   ```

   Then open a PR against `azstrait/yomama-api:main`.

Please describe:

- What you changed.
- Why you changed it.
- Any relevant notes for reviewers.

The CI workflow will automatically run lint and tests on your PR.

---

## Adding or Editing Jokes

Jokes live in a CSV/TSV file with columns:

```csv
id,joke,category
```

### Schema Rules

1. `id`:
   - Must be an **unquoted integer**.
   - Must be unique.

2. `joke`:
   - Must be enclosed in **double quotes**.
   - Must begin with one of:
     - `Yo mama is`
     - `Yo mama's <noun>`
   - Any internal commas are fine as long as the field is quoted.

3. `category`:
   - Must be enclosed in **double quotes**.
   - Should be a lowercase, single-word category where possible (e.g. `old`, `fat`, `ugly`, `nerd`).

### Example

```csv
1,"Yo mama is so old, her first car was a chariot.","old"
2,"Yo mama is so fat, when she sits around the house, she sits AROUND the house.","fat"
3,"Yo mama's teeth are so yellow, when she smiles, traffic slows down.","ugly"
```

### Guidelines

- Aim for jokes that are in the spirit of classic “Yo Mama” jokes.
- Avoid hate speech, slurs, or anything targeting real individuals or protected groups.
- Categories should be descriptive but not derogatory whenever possible.

---

## Style & Code Guidelines

- Use `black` for Python formatting.
- Keep frontend JS/HTML consistent with the current style.
- Favor small, focused changes per PR.
- If you’re making significant changes to behavior or configuration, please also update:
  - `README.md`
  - Any relevant tests.

---

## Questions

If you’re unsure about anything (joke formatting, code structure, tests), feel free to:

- Open a draft PR and ask in the PR description.
- Or open an issue with your question and context.

Thanks for contributing to **Yo Mama Jokes API**!