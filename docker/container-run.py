import os
from pathlib import Path

import uvicorn
from app.config import get_settings


def main():
    settings = get_settings()

    # Determine which jokes file exists in DATA_DIR
    data_dir = settings.DATA_DIR
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    csv_path = data_dir / settings.JOKES_CSV_FILENAME
    tsv_path = data_dir / settings.JOKES_TSV_FILENAME

    reload_dirs = []
    reload_includes = []

    if csv_path.is_file():
        # Watch just the csv file
        reload_dirs = [str(csv_path.parent)]
        reload_includes = [str(csv_path.name)]
    elif tsv_path.is_file():
        # Watch just the tsv file
        reload_dirs = [str(tsv_path.parent)]
        reload_includes = [str(tsv_path.name)]
    else:
        # If no jokes file exists yet, just watch the data dir for when one appears
        reload_dirs = [str(data_dir)]
        reload_includes = ["*.csv", "*.tsv"]

    # Allow overriding reload behavior via env (e.g., RELOAD=false)
    reload_env = os.getenv("RELOAD", "true").lower()
    reload_flag = reload_env in ("1", "true", "yes")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=reload_flag,
        access_log=False,
        log_level=settings.LOG_LEVEL.lower(),
        reload_dirs=reload_dirs,
        reload_includes=reload_includes,
    )


if __name__ == "__main__":
    main()
