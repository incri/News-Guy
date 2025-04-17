from sqlalchemy import create_engine
from app.database.models import Base
from app.config import get_settings

settings = get_settings()


def init_db():
    """Initialize the database with required tables."""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
