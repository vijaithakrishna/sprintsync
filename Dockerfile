FROM python:3.11-slim

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD alembic upgrade head && python seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000