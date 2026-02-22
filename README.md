# SprintSync

A lean sprint management tool with AI-assisted task descriptions.

## Live Demo
- **Frontend:** https://sprintsync-front.netlify.app/frontend.html
- **API:** https://sprintsync-api-fvs3.onrender.com
- **Swagger Docs:** https://sprintsync-api-fvs3.onrender.com/docs
- **Metrics:** https://sprintsync-api-fvs3.onrender.com/metrics

## Demo Accounts
| Email | Password | Role |
|-------|----------|------|
| admin@sprintsync.dev | admin123 | Admin |
| alice@sprintsync.dev | alice123 | User |
| bob@sprintsync.dev | bob123 | User |

## Tech Stack
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy + Alembic
- **Auth:** JWT (python-jose) + bcrypt
- **AI:** Groq API (llama-3.1-8b-instant)
- **Frontend:** Vanilla HTML/CSS/JS
- **Deploy:** Render (API + DB) + Netlify (Frontend)
- **Tests:** pytest + httpx (7 tests)

## Architecture
```
Browser (Netlify)
    ? HTTPS
FastAPI (Render Docker)
    ? JWT Auth + Pydantic Validation
    ? SQLAlchemy ORM
PostgreSQL (Render)
    ? AI Suggest
Groq API (llama-3.1)
```

## Local Setup
```bash
# Clone repo
git clone https://github.com/vijaithakrishna/sprintsync
cd sprintsync

# Create venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements-backend.txt

# Start database
docker-compose up db -d

# Run migrations
alembic upgrade head
python seed.py

# Start server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register user |
| POST | /auth/login | Login + get JWT |
| GET | /users/me | Current user |
| GET/POST | /tasks/ | List/Create tasks |
| PATCH | /tasks/{id}/status | Advance status |
| POST | /ai/suggest | AI description |
| GET | /metrics | Observability |

## Video Demo
[Loom Video Link Here]