#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "app" / "version.py"

VERSION_RE = re.compile(r'^__version__\s*=\s*["\'](?P<version>\d+\.\d+\.\d+)["\']\s*$', re.MULTILINE)


def get_current_version() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if not m:
        raise RuntimeError(f"Could not find __version__ in {VERSION_FILE}")
    return m.group("version")


def set_version(new_version: str) -> None:
    text = VERSION_FILE.read_text(encoding="utf-8")
    new_text = VERSION_RE.sub(f'__version__ = "{new_version}"', text)
    VERSION_FILE.write_text(new_text, encoding="utf-8")


def bump_part(version: str, part: str) -> str:
    major, minor, patch = map(int, version.split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError("part must be one of: major, minor, patch")
    return f"{major}.{minor}.{patch}"


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"major", "minor", "patch"}:
        print("Usage: bump_version.py [major|minor|patch]")
        sys.exit(1)

    part = sys.argv[1]
    current = get_current_version()
    new = bump_part(current, part)

    print(f"Bumping version: {current} -> {new}")
    set_version(new)

    # git commit and tag
    subprocess.check_call(["git", "add", str(VERSION_FILE)])
    subprocess.check_call(["git", "commit", "-m", f"chore: bump version to v{new}"])
    subprocess.check_call(["git", "tag", f"v{new}"])

    print(f"Created tag v{new}. You can now push with:")
    print(f"  git push && git push origin v{new}")


if __name__ == "__main__":
    main()