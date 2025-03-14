from sqlalchemy.ext.asyncio import AsyncSession

from database.async_redis import CacheDB
from database.database import get_session
from fastapi import Depends

from repositories import UserRepository, PostRepository

from models.user import User
from models.post import Post

from services import UserService, PostService


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
	return UserService(
		user_repo=UserRepository(session, User)
	)


def get_post_service(session: AsyncSession = Depends(get_session)) -> PostService:
	return PostService(
		post_repo=PostRepository(session, Post),
		redis=CacheDB()
	)
