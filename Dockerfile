# lawdz Django container
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for PDF + Arabic
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Collect static (will be empty for API mostly)
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# Default command (overridden in compose)
CMD ["gunicorn", "lawdz.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
