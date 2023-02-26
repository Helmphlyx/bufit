import os


class Settings:
    """Global settings."""

    MYSQL_CREDENTIALS = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("RDS_DB_NAME"),
        "USER": os.environ.get("RDS_USERNAME"),
        "PASSWORD": os.environ.get("RDS_PASSWORD"),
        "HOST": os.environ.get("RDS_HOSTNAME"),
        "PORT": os.environ.get("RDS_PORT"),
    }

    DATABASE_SHORT_NAME = MYSQL_CREDENTIALS["NAME"] or "database.db"
    DATABASE_NAME = (
        MYSQL_CREDENTIALS["NAME"] or f"instance/{DATABASE_SHORT_NAME}"
    )


settings = Settings()
