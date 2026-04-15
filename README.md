# Yo Mama Jokes API

A self-hostable RESTful web app + API for “Yo Mama” jokes, powered by FastAPI and backed by a simple CSV/TSV file.

- Live website UI: lets you pick a category (or any category) and fetch jokes with a single click.
- JSON API: `/api/random`, `/api/random/{category}`, and `/api/categories`.
- Swagger/OpenAPI docs: `/docs`.
- Self-hostable via Docker (with a bind-mounted `data` directory you can edit).
- Reads from a simple `jokes.csv` / `jokes.tsv` file.

If you use [The Lounge](https://thelounge.chat/), check out the companion plugin:

> **TheLounge Plugin**: [`thelounge-plugin-yomama`](https://github.com/azstrait/thelounge-plugin-yomama)

---

## Features

- FastAPI backend with auto-generated Swagger UI at `/docs`.
- Simple HTML/JS frontend at `/`:
  - Category dropdown (or “Any category”).
  - “Get Random Joke” button.
  - “Copy Joke” button. (only works on secure connections, `http://localhost`, and `http://127.0.0.1`)
- Jokes stored in `jokes.csv` (or `jokes.tsv`).
- API responses:
  - `GET /api/random` → random joke (any category).
  - `GET /api/random/{category}` → random joke in that category.
  - `GET /api/categories` → list of categories + count.
  - `GET /health` → health and basic stats.
- Optional link from UI to the full jokes file (CSV/TSV) if enabled.

---

## API Overview

- `GET /api/random`  
  Returns a JSON object:
  ```json
  {
    "status": "success",
    "id": 42,
    "joke": "Yo mama is so old, her first car was a chariot.",
    "category": "old"
  }
  ```

- `GET /api/random/{category}`  
  Returns a random joke within `category`, or 404 if not found:
  ```json
  {
    "status": "failure",
    "message": "Category not found or has no jokes"
  }
  ```

- `GET /api/categories`  
  Returns all categories and a count:
  ```json
  {
    "status": "success",
    "categories": ["old", "fat", "ugly"],
    "category_count": 3
  }
  ```

- `GET /health`  
  Basic health info:
  ```json
  {
    "status": "ok",
    "app_name": "Yo Mama Jokes API",
    "version": "1.0.0",
    "jokes_loaded": true,
    "joke_count": 123,
    "category_count": 7,
    "environment": "production"
  }
  ```

---

## Running via Docker

### Example `docker-compose.yml`

```yaml
name: yomama
services:
  yomama-api:
    image: ghcr.io/azstrait/yomama-api:latest
    container_name: yomama-api
    ports:
      - "6262:6262"
    environment:
        # the directory (inside the container) where it looks for jokes.csv
      - DATA_DIR=/data
        # the port the UI runs on
      - PORT=6262
        # Can be one of: debug, info, warning, error, critical
      - LOG_LEVEL=info            # case-insensitive (info/INFO/Info)
        # whether to include a link to jokes.csv on the homepage
      - DOWNLOADABLE_JOKES=true   # case-insensitive (true/1/yes/...)
      - RELOAD=true               # watches jokes.csv file for changes
                                  # and reloads the API automatically
    volumes:
      - ./data:/data              # jokes.csv will be created here if absent
    restart: unless-stopped
```

Usage:

```bash
mkdir -p data
docker compose up -d
```

On first startup, if `./data` contains no `.csv` or `.tsv`, the container will seed `./data/jokes.csv` from the bundled default list. You can then edit `./data/jokes.csv` on the host.

By default (`RELOAD=true`), the container watches the jokes file (`jokes.csv`/`jokes.tsv`) for changes and will reload the app when it changes, so new jokes can be picked up live. If you'd like to disable this behavior, set `RELOAD=false`.

### Example `docker run` command

```bash
mkdir -p data

docker run -d \
  --name yomama-api \
  -p 6262:6262 \
  -e DOWNLOADABLE_JOKES=true \
  -e RELOAD=true \
  -v "$(pwd)/data:/data" \
  ghcr.io/azstrait/yomama-api
```

Then visit: `http://localhost:6262/`

---

## Running from Source

Requirements:

- Python **3.8+**
- Git
- A terminal and basic familiarity with virtual environments.

### 1. Clone the repository

```bash
git clone https://github.com/azstrait/yomama-api.git
cd yomama-api
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate     # on Linux/macOS

# on Windows (PowerShell):
# python -m venv .venv
# .venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ensure jokes data exists

By default, the app expects a `data/` directory and a `jokes.csv` or `jokes.tsv` inside it.

CSV format:

```csv
id,joke,category
1,"Yo mama so old, her first car was a chariot.","old"
2,"Yo mama so fat, when she sits around the house, she sits AROUND the house.","fat"
```
> [!NOTE]
> Be sure to encase jokes with double quotes so any commas contained in them don't break the CSV formatting.

### 5. Run the app (development)

Use the dev runner (`run.py`) which enables FastAPI/Uvicorn reload:

```bash
python run.py
```

By default:

- Listens on `http://0.0.0.0:6262`. (`PORT=6262`)
- Reloads on code changes.
- Logs at `LOG_LEVEL` (default: `INFO`).
- Environment variable can be set by running them before `python run.py`:
  ```bash
  LOG_LEVEL=warning python run.py
  ```

Visit:

- `http://localhost:6262/` – Web UI.
- `http://localhost:6262/docs` – Swagger UI/API docs.

### 6. Run tests

```bash
pytest
```

---

## Environment Variables

These can be used both:

- **From source** (via shell env vars before running `run.py`).
- **In Docker** (via `environment:` in compose or `-e` in `docker run`).

| Variable             | Default  | Description                                                                                          | Possible values                                     |
|----------------------|----------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `DATA_DIR`           | `/data`  | Directory containing `jokes.csv` or `jokes.tsv`. In Docker, the container side of a bind mount.          | Any valid directory path.                           |
| `JOKES_CSV_FILENAME` | `jokes.csv` | Name of the CSV jokes file within `DATA_DIR`.                                                       | Any filename; must match actual file.               |
| `JOKES_TSV_FILENAME` | `jokes.tsv` | Name of the TSV jokes file within `DATA_DIR`.                                                       | Any filename; must match actual file.               |
| `DOWNLOADABLE_JOKES` | `false`  | Whether the UI and `/data/jokes` endpoint expose the jokes file.                                     | `true`, `1`, `yes`, `y` → enabled; anything else → disabled. Case-insensitive. |
| `PORT`               | `6262`   | TCP port the app listens on.                                                                         | Any valid port (e.g. `8000`, `8080`).               |
| `LOG_LEVEL`          | `INFO`   | Logging level for the app and Uvicorn.                                                              | `debug`, `info`, `warning`, `error`, `critical` (case-insensitive). |
| `RELOAD`             | `true` (in container-run) / controlled by `run.py` in dev | In container mode, controls whether Uvicorn reloads on changes to jokes file. In dev `run.py`, reload is always on. | `true`, `1`, `yes`, `y` → reload enabled; anything else → disabled. |
| `ENVIRONMENT`        | `production` (currently unused but available in health) | Optional environment label used in `/health` if you choose to wire it.                          | e.g. `development`, `staging`, `production`.        |

Notes:

- `DATA_DIR` is used by both the app and the Docker entrypoint. In Docker, the entrypoint will:
  - Create `${DATA_DIR}` inside the container if missing.
  - Seed `jokes.csv` from `app/default_jokes.csv` if no `*.csv` or `*.tsv` exists.
- `DOWNLOADABLE_JOKES`:
  - If `true`, the homepage shows a “See full list here.” link and the `/data/jokes` endpoint returns the CSV/TSV inline.
  - If `false`, `/data/jokes` returns 404 and the link is omitted.

---

## Version Tagging and Docker Images

The repository uses semantic-style version tags to drive Docker builds via GitHub Actions.

The “Docker Publish” workflow will:

1. Run lint (Black) and tests (pytest).
2. Build a multi-arch image (`linux/amd64`, `linux/arm64`) from `docker/Dockerfile`.
3. Push the image to GHCR with the following tags:

- `ghcr.io/azstrait/yomama-api:v1`
- `ghcr.io/azstrait/yomama-api:v1.2`
- `ghcr.io/azstrait/yomama-api:v1.2.3`
- `ghcr.io/azstrait/yomama-api:latest`
- `ghcr.io/azstrait/yomama-api:build-<short-commit>`

This makes it easy to pin:

- Major only: `v1`
- Minor: `v1.2`
- Exact patch: `v1.2.3`
- Or always follow the latest: `latest`.

Non-tag pushes/PRs do **not** publish images; they only run the “CI” workflow (lint + tests).

---

## Contributing

Contributions are welcome!

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
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:

   ```bash
   pytest
   ```

4. Lint:

   ```bash
   black .
   ```

### 3. Make Your Changes

- Create a feature branch:

  ```bash
  git checkout -b feature/my-cool-thing
  ```

- Modify code, templates, or jokes.
- Update or add tests.
- Ensure:

  ```bash
  black .
  pytest
  ```

  both succeed.

### 4. Open a Pull Request

- Push your branch:

  ```bash
  git push origin feature/my-cool-thing
  ```

- Open a PR against `azstrait/yomama-api:main`.
- Describe:
  - What you changed.
  - Why you changed it.
  - Any relevant notes.

The CI workflow will automatically run lint and tests on your PR.

---

## Credits and References

This project is heavily inspired by and based on earlier work by:

- **GitHub user:** [@laffchem](https://github.com/laffchem)
  - Original repo: <https://github.com/laffchem/yomama>
  - Original website: <https://www.yomama-jokes.com/>

This implementation reworks the architecture around FastAPI, updates the web UI, adds Docker support and CI/CD, while preserving the spirit of the original project.

---