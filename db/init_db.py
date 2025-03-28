import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from models.db_models import Base
from config import settings

CREATE_DB_URL = settings.DATABASE_URL.replace("journey_db", "defaultdb")
JOURNEY_DB_NAME = "journey_db"


def create_database_if_not_exists():
    print("🔧 Connecting to defaultdb to ensure journey_db exists...")
    engine = create_engine(
        CREATE_DB_URL,
        connect_args={"sslmode": "disable"},
        execution_options={"isolation_level": "AUTOCOMMIT"},
    )
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {JOURNEY_DB_NAME}"))
        print(f"Created database {JOURNEY_DB_NAME} (or it already exists).")
    engine.dispose()


def wait_until_db_ready():
    print("Waiting for journey_db to be ready...")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"sslmode": "disable"},
    )
    for _ in range(10):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("journey_db is ready.")
                return
        except OperationalError as e:
            print("...still waiting for journey_db to come online...")
            time.sleep(2)
    raise RuntimeError("journey_db not ready after multiple attempts")


def init():
    create_database_if_not_exists()
    wait_until_db_ready()

    print("Creating schema...")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"sslmode": "disable"},
    )
    Base.metadata.create_all(bind=engine)
    engine.dispose()
    print("Schema setup complete.")


if __name__ == "__main__":
    init()
