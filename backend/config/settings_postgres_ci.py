"""CI-only PostgreSQL settings.

This module is intentionally separate from production settings so the
PostgreSQL verification job cannot silently change deployment database
selection.
"""
import os

from .settings import *  # noqa: F401,F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "zootasks_ci"),
        "USER": os.environ.get("POSTGRES_USER", "zootasks_ci"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "zootasks_ci_password"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
}
