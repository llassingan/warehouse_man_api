FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code (FastAPI + Alembic)
COPY api/ ./ 

# Default CMD (can be overridden by docker-compose)
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]
