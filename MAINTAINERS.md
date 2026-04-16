## Maintainer Notes (Release Process)

For maintainers only:

- Version is defined in `app/version.py` as `__version__ = "X.Y.Z"`.
- There is a helper script `scripts/bump_version.py` to bump version and tag:
  - `python scripts/bump_version.py patch`  # or minor/major
  - `git push && git push origin vX.Y.Z`
- GitHub Actions (`publish.yml`) will:
  - Run tests & lint
  - Build and push Docker images
  - Create a GitHub Release with a changelog