from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from .post import Post


class User(Base):
	__tablename__ = 'users'

	id = Column("id", Integer, primary_key=True, index=True)

	login: Mapped[str] = mapped_column()
	password_sha256: Mapped[str] = mapped_column('password')

	posts: Mapped[list[Post]] = relationship('Post', back_populates="user", cascade="all, delete-orphan")
