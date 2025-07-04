from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session(db_file: str):
    engine = create_engine(f"sqlite:///{db_file}", echo=True, future=True)
    return sessionmaker(bind=engine, autoflush=False)
