from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from .user import User


class Post(Base):
	__tablename__ = 'applications'

	id = Column("id", Integer, primary_key=True, index=True)

	user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

	text: Mapped[str] = mapped_column()

	user: Mapped[User] = relationship('User', back_populates="posts")
