# e-Learning Platform Backend (FastAPI)

A lightweight FastAPI starter template featuring modular design patterns, JWT token-based authentication, and a simple local JSON file database backup.

## Project Structure
- `app/`: Core application files.
  - `core/`: Base configuration, security (password/JWT operations), and JSON database read/write helpers.
  - `schema/`: Pydantic model schemas for validation of endpoints' inputs and outputs.
  - `v1/`: API route versioning (e.g. auth routes, health routes).
  - `deps.py`: Shared FastAPI dependency injection functions.
  - `main.py`: App initiation, routing configuration, CORS policies, etc.
- `test/`: Integration and unit tests using `pytest` and `httpx.AsyncClient`.
- `data/`: Local storage for the lightweight JSON database.

## Quickstart

### 1. Requirements & Setup
Ensure you have Python 3.9+ installed.

```bash
# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run the Server
Start the development server using:
```bash
uvicorn app.main:app --reload
```
The documentation will be available locally at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 4. Running Tests
Run pytest to verify the endpoints function correctly:
```bash
pytest
```
