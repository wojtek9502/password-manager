from sqlalchemy.orm import sessionmaker

from src import engine

SessionLocal = sessionmaker(autocommit=False, bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
