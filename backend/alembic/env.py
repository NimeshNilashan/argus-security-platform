# Alembic migration configuration.

import os
import sys

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv


# Add backend directory to Python path.
# This allows importing the app package.
sys.path.append(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


# Load environment variables.
load_dotenv()


# Import SQLAlchemy Base.
from app.config.base import Base


# Import all models.
# Without this, Alembic will not detect tables.
from app.models import (
    User,
    Scan,
    Finding,
    FIMBaseline
)


config = context.config


# Setup logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic about our models.
target_metadata = Base.metadata


# Read database URL from .env.
DATABASE_URL = os.getenv("DATABASE_URL")

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


def run_migrations_offline():
    """
    Run migrations without connecting to database.
    """

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online():
    """
    Run migrations using database connection.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )


        with context.begin_transaction():
            context.run_migrations()



if context.is_offline_mode():
    run_migrations_offline()

else:
    run_migrations_online()