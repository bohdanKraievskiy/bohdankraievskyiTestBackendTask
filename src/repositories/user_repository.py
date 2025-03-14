from models.user import User

from utils.I_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[User]):
	def __init__(self, db_session: AsyncSession, model: User):
		super().__init__(db_session, model)
