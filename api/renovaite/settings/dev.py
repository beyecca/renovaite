import os

from .base import *  # noqa: F401, F403
from .base import BASE_DIR  # noqa: F401

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
