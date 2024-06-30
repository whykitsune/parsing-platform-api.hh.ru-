from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class VacanciesTable(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    salary: Mapped[str]
    employer: Mapped[str]
    experience: Mapped[str]
    employment: Mapped[str]
    schedule: Mapped[str]
    area: Mapped[str]
    key_skills: Mapped[str]
    description: Mapped[str]
    url: Mapped[str]
