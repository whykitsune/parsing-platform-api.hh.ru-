from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

engine = create_engine(
    url=settings.database_url
)

session_factory = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
