from sqlalchemy.orm import sessionmaker, scoped_session

from src import engine

session_factory = sessionmaker(autocommit=False, bind=engine)
Session = scoped_session(session_factory)


def get_db_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
