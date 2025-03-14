from models.post import Post

from utils.I_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PostRepository(BaseRepository[Post]):
	def __init__(self, db_session: AsyncSession, model: Post):
		super().__init__(db_session, model)
