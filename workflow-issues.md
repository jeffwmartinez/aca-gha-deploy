# Portal workflow review

This file summarizes issues in the portal-generated build-and-deploy workflow and why it fails in this repo.

## What went wrong

- Registry URL is empty.
  - The action expects `registryUrl` to be set (for example, `myregistry.azurecr.io`). Leaving it blank causes the build/push step to fail.
- Dockerfile path placeholders were left in the file.
  - `_dockerfilePathKey_`, `_dockerfilePath_`, `_targetLabelKey_`, `_targetLabel_`, and `_buildArgumentsKey_` are portal placeholders, not valid inputs for the action. They should be removed or replaced with real values (for example, `dockerfilePath: ./Dockerfile`).
- The repo has no Dockerfile or container config.
  - The action builds an image from source, but this repo intentionally has no container configuration yet, so the build fails even if the inputs were correct.
- `imageToBuild` is not a valid image reference.
  - `default/[parameters('containerAppName')]:${{ github.sha }}` includes ARM template syntax and does not resolve in GitHub Actions. It must be a real registry image, e.g. `myregistry.azurecr.io/jefmarti-aca-gha:${{ github.sha }}`.

## What to fix later

- Add a Dockerfile or switch to deploying an already built image.
- Provide `registryUrl`, `registryUsername`, and `registryPassword` (or use OIDC with ACR) and a valid `imageToBuild`.
- Remove all portal placeholder keys and supply only supported action inputs.
