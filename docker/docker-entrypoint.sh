#!/usr/bin/env sh
set -e

# Normalize case-insensitive env vars
if [ -n "${LOG_LEVEL}" ]; then
  # shellcheck disable=SC2155
  export LOG_LEVEL="$(printf '%s' "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')"
else
  export LOG_LEVEL="info"
fi

case "$(printf '%s' "$DOWNLOADABLE_JOKES" | tr '[:upper:]' '[:lower:]')" in
  "true"|"1"|"yes"|"y") export DOWNLOADABLE_JOKES="true" ;;
  *) export DOWNLOADABLE_JOKES="false" ;;
esac

if [ -z "${DATA_DIR}" ]; then
  export DATA_DIR="/data"
fi

# Ensure DATA_DIR exists
mkdir -p "${DATA_DIR}"

# Seed jokes file if missing
if ! find "${DATA_DIR}" -maxdepth 1 -type f \( -name "*.csv" -o -name "*.tsv" \) | grep -q .; then
  echo "No jokes CSV/TSV found in ${DATA_DIR}, seeding with default jokes.csv"
  cp /app/app/default_jokes.csv "${DATA_DIR}/jokes.csv"
fi

# Ensure appuser owns DATA_DIR (so the app can read/write if needed)
chown -R appuser:appuser "${DATA_DIR}"

# Drop privileges to appuser and run the app
exec su appuser -s /bin/sh -c "cd /app && python container-run.py"