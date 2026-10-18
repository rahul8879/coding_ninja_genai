from app.db.database import engine
from app.db.models import Base


def main():
    with engine.begin() as connection:
        Base.metadata.create_all(connection)
    print("Database tables are ready.")


if __name__ == "__main__":
    main()