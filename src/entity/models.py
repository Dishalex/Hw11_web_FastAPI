from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, Enum
from sqlalchemy.types import Date

from sqlalchemy.orm import DeclarativeBase, relationship

import enum

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
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=True, default=1)
    user = relationship("User", backref='contacts', lazy='joined')


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    role = Column("role", Enum(Role), default=Role.user, nullable=True)
    confirmed = Column(Boolean, default=False, nullable=True)
