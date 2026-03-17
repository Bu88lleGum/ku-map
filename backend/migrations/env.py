import sys
from os.path import abspath, dirname
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем путь к приложению
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from app.models import metadata 
from app.core.database import DATABASE_URL

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata

def include_object(object, name, type_, reflected, compare_to):
    # Разрешаем только наши таблицы из ER-диаграммы
    MY_PROJECT_TABLES = ["node", "edge", "wall", "alembic_version"]
    # Игнорируем авто-индексы геометрии (PostGIS создаст их сам)
    IGNORE_INDEXES = ["idx_node_geom", "idx_wall_geom"]

    if type_ == "table":
        return name in MY_PROJECT_TABLES
    if type_ == "index":
        return name not in IGNORE_INDEXES
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object # <--- Фильтр здесь
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object # <--- И здесь
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()