# OLM CI Image

Ollama model images for CI workflows.

## Workflow snapshot

- Reusable workflow: `.github/workflows/push.yml`
  - `generate-matrix` parses `src/models.json` with `jq` and emits one job per model plus a `latest` tag.
  - `build-and-push` uses Buildx to publish multi-arch images tagged as `ghcr.io/<owner>/olm-ci-img:<alias>-<version>` and `:latest` for the alias set in `latest.alias`.
- Trigger this repo from another workflow with:

  ```yaml
  jobs:
    push-images:
      uses: Astra-Teams/olm-ci-img/.github/workflows/push.yml@main
  ```

## Updating models

- Edit `src/models.json`:
  - `models.<alias>.name` holds the exact `ollama` model reference pulled during the build.
  - `latest_version` sets the version suffix added to every tag.
  - `latest.alias` decides which model also receives the `latest` tag.
- Commit and let the calling workflow rebuild/push.

## Local sanity checks (optional)

- `just test` runs the pytest suite, building the image in CI-like conditions.
- `just format` / `just lint` wrap `black` and `ruff` for quick hygiene fixes.