FROM python:3.12-slim

WORKDIR /app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Collect static assets into the image. Railway pre-deploy containers are
# separate and their filesystem changes do not persist to the application.
RUN SECRET_KEY=build-only-zootasks-static-collection \
    ALLOWED_HOSTS=localhost \
    PRODUCTION_MODE=False \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
