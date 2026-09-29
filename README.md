# se-mapspec

[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-mapspec/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-mapspec)
[![Python 3.15+](https://img.shields.io/badge/python-3.15%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/structural-explainability/se-mapspec/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-mapspec/actions/workflows/ci-python-zensical.yml)
[![Docs](https://github.com/structural-explainability/se-mapspec/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-mapspec/actions/workflows/deploy-zensical.yml)
[![Links](https://github.com/structural-explainability/se-mapspec/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-mapspec/actions/workflows/links.yml)

> Structural Explainability MapSpec:
> mapping vocabulary and structural correspondence rules for the SE ecosystem.

## Context

- se-constitution defines rules
- se-kernel defines primitives those rules depend on
- se-admin enforces rules across repositories
- se-mapspec defines how structures correspond across systems

## Owns

- mapping vocabulary
- mapping relation patterns
- constraints for expressing mappings between artifacts

## Includes

### mapping primitives

- source-target relationships
- correspondence identifiers

### mapping structure

- how mappings are declared
- how elements align across systems

### mapping constraints

- allowed mapping forms
- structural consistency requirements

### reference patterns

- stable references between mapped elements

## Elsewhere

- se-mapping-\*
- se-adapter-\*

Other projects will provide:

- adapters
- runtime transformations
- runtime connectors
- data processing logic
- domain semantics

## Development

### Clone and Open in VS Code

```shell
git clone https://github.com/structural-explainability/se-mapspec

cd se-mapspec
code .
```

### Set Up the Project

```shell
uvx pup-clean --delete
uv self update
uv python install
uv lock --upgrade
uv sync
uv audit

# set up and run git hooks
uv run prek install --force
uv run prek update
git add -A
uv run prek run --all-files
# repeat if changes were made
uv run prek run --all-files

# run the module
uv run python -m se_mapspec

# do chores
npx markdownlint-cli "**/*.md" --fix
uv run python -m ruff format .
uv run python -m ruff check . --fix
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

## Citation

[CITATION.cff](./CITATION.cff)

## License

[LICENSE](./LICENSE)

## Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
