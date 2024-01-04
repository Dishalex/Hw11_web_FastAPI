from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.types import Date

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass



class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(25), index=True, nullable=False)
    last_name = Column(String(25))
    email = Column(String(50), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), default="None", nullable=False)
    birth_date = Column(Date, nullable=True)
    additional_data = Column(String, default="None", nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())