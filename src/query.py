from src.database import engine, Base


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
