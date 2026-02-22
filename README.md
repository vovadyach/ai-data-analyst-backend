# AI Data Analyst API

Backend service for AI-powered data analysis. Upload CSV/Excel files, ask questions, get insights and charts.

## Tech Stack
- FastAPI
- SQLAlchemy + PostgreSQL
- Alembic (migrations)
- Google Gemini AI

## Setup

### Prerequisites
- Python 3.12+
- Docker Desktop

### Quick Start
```bash
# 1. Clone
git clone <repo-url>
cd ai-data-analyst-backend

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Start database
docker compose up -d

# 4. Run migrations
alembic upgrade head

# 5. Start server
fastapi dev app/main.py
```

## API Docs
Available at http://localhost:8000/docs

## Status
🚧 Work in progress