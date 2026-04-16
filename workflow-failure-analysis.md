# ACA workflow failure analysis (current attempt)

## Summary

The GitHub Actions workflow completed successfully, but the newest Container App revision still fails to start. The revision is created with an explicit `uvicorn` command and args, so the failure is now happening at container runtime rather than during build/push/deploy.

## Evidence

- Latest run: succeeded (no build/push/deploy errors).
- Latest revision: `jxm-aca-actions-app--0000005`
  - `provisioningState`: Failed
  - `runningStateDetails`: `1/1 Container crashing: jxm-aca-actions-app`
  - Container command/args:
    - `command`: `uvicorn`
    - `args`: `app.main:app --host 0.0.0.0 --port 8000`
  - Image: `jxmacareg.azurecr.io/gh-action/container-app:latest`

## Likely failure causes

1. **Overriding the command bypasses Oryx startup behavior.**
   The buildpack image normally uses Oryx’s startup script that activates the virtual environment and sets PATH/PYTHONPATH. Forcing `uvicorn` directly can fail if dependencies or the app module are not on the default PATH at runtime.
2. **Runtime cannot import the app module.**
   Even with `uvicorn app.main:app`, the container may not have the working directory or PYTHONPATH set to the app source directory inside the Oryx-built image.
3. **Missing runtime logs for the crash.**
   The container crashes quickly, and the log stream shows connection only. The actual stack trace is likely emitted before the log stream is attached.

## Why this is different from the previous failures

- Earlier failures were due to auth/registry issues and env-var parsing.
- This attempt successfully builds and deploys the image, but the container cannot start with the override command.

## What this implies

The Oryx buildpack image is not reliable for this workflow if we need a deterministic runtime command. A Dockerfile that explicitly sets the working directory and entrypoint would remove this ambiguity.

## Current workflow file

```yaml
name: Trigger auto deployment for jefmarti-aca-gha

on:
  push:
    branches: 
      [ main ]
    paths:
    - '**'
    - '.github/workflows/jefmarti-aca-gha-AutoDeployTrigger-0a925bac-652d-4876-a51d-210466534b75.yml'

  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions: 
      id-token: write #Not used when creds auth is configured
      contents: read #Required when GH token is used to authenticate with private repo
    env:
      ACA_RESOURCE_GROUP: ${{ vars.ACA_RESOURCE_GROUP }}
      ACA_APP_NAME: ${{ vars.ACA_APP_NAME }}
      ACA_ENV_NAME: ${{ vars.ACA_ENV_NAME }}
      ACA_ACR_NAME: ${{ vars.ACA_ACR_NAME }}
      ACA_LOCATION: ${{ vars.ACA_LOCATION }}
      ACA_TARGET_PORT: ${{ vars.ACA_TARGET_PORT || '8000' }}

    steps:
      - name: Checkout to the branch
        uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v3
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push container image to registry
        uses: azure/container-apps-deploy-action@v2
        with:
          appSourcePath: ${{ github.workspace }}
          acrName: ${{ env.ACA_ACR_NAME }}
          acrUsername: ${{ secrets.ACR_USERNAME }}
          acrPassword: ${{ secrets.ACR_PASSWORD }}
          imageToBuild: ${{ env.ACA_ACR_NAME }}.azurecr.io/gh-action/container-app:latest
          containerAppName: ${{ env.ACA_APP_NAME }}
          resourceGroup: ${{ env.ACA_RESOURCE_GROUP }}
          containerAppEnvironment: ${{ env.ACA_ENV_NAME }}
          location: ${{ env.ACA_LOCATION }}
          ingress: external
          targetPort: ${{ env.ACA_TARGET_PORT }}
          runtimeStack: "python:3.11"
          environmentVariables: PORT=${{ env.ACA_TARGET_PORT }}
          yamlConfigPath: ${{ github.workspace }}/aca-containerapp.yaml
```
