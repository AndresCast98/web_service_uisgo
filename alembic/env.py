from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os, sys
from pathlib import Path

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)




BASE_DIR = Path(__file__).resolve().parents[1]  # carpeta raíz del repo (donde está 'alembic/')
REPO_ROOT = BASE_DIR  # ajusta si tu layout es distinto
BACKEND_DIR = REPO_ROOT / "Backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from Backend.app.core.config import settings
from Backend.app.db.base import Base
import Backend.app.models  # noqa

config = context.config
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
