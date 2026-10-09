FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# The repository keeps Django code and requirements under backend/.
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

EXPOSE 8000

# Run collectstatic with runtime environment variables available, then start
# Gunicorn on the port supplied by the hosting platform.
CMD ["sh", "-c", "python manage.py collectstatic --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:\${PORT:-8000}"]
