# FastAPI Web App (Azure-ready)

Simple FastAPI app intended for hosting on Azure later (e.g., Azure Container Apps).

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Start the app:

   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

4. Open:

   http://localhost:8000/

## Endpoints

- GET / -> basic response
- GET /healthz -> health check

## Notes

- No container configuration yet, per request.
