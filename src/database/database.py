from sqlalchemy import create_engine, func
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL
import dataclasses
import logging


from functools import partial
from config import Config, get_config


class Base(DeclarativeBase):
	pass


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session = sessionmaker(
	bind=async_engine,
	class_=AsyncSession,
	expire_on_commit=False
)


async def get_db():
	async with async_session() as session:
		try:
			yield session
		finally:
			await session.close()


@dataclasses.dataclass
class DBSettings:
	database_url: str

	db_engine_pool_pre_ping: bool = True
	db_engine_pool_recycle: int = -1
	db_engine_pool_size: int = 5
	db_engine_max_overflow: int = 10
	db_engine_pool_timeout: int = 30
	sql_engine_echo: bool = False
	application_name: str = 'Backend Application'

	def __hash__(self):
		return hash(self.database_url + str(self.sql_engine_echo))


class SQLAlchemyManager:
	logger = logging.getLogger("sqlalchemy")
	_engines = {}

	@classmethod
	def get_engine(cls, settings: DBSettings) -> Engine:
		if settings in cls._engines:
			return cls._engines[settings]

		cls.logger.info("Create sync engine", extra=dataclasses.asdict(settings))

		engine = create_engine(
			settings.database_url.replace("+asyncpg", ""),
			connect_args={"application_name": settings.application_name},
			max_overflow=settings.db_engine_max_overflow,
			pool_pre_ping=settings.db_engine_pool_pre_ping,
			pool_recycle=settings.db_engine_pool_recycle,
			pool_size=settings.db_engine_pool_size,
			pool_timeout=settings.db_engine_pool_timeout,
			echo=settings.sql_engine_echo,
		)

		cls._engines[settings] = engine
		return engine

	@classmethod
	def get_async_engine(cls, settings: DBSettings) -> AsyncEngine:
		if settings in cls._engines:
			return cls._engines[settings]

		cls.logger.info("Create async engine", extra=dataclasses.asdict(settings))

		engine = create_async_engine(
			settings.database_url,
			max_overflow=settings.db_engine_max_overflow,
			pool_pre_ping=settings.db_engine_pool_pre_ping,
			pool_recycle=settings.db_engine_pool_recycle,
			pool_size=settings.db_engine_pool_size,
			pool_timeout=settings.db_engine_pool_timeout,
			echo=settings.sql_engine_echo,
		)

		cls._engines[settings] = engine
		return engine

	@classmethod
	def get_async_session(cls, db_settings: DBSettings) -> AsyncSession:
		return AsyncSession(
			bind=cls.get_async_engine(db_settings),
			autoflush=True,
			autocommit=False,
			expire_on_commit=False,
		)

	@classmethod
	def get_session(cls, db_settings: DBSettings) -> Session:
		return Session(
			bind=cls.get_engine(db_settings),
			autoflush=True,
			autocommit=False,
			expire_on_commit=False,
		)

	@classmethod
	def get_async_session_generator(cls, db_settings: DBSettings):
		async def _get_session():
			async with cls.get_async_session(db_settings) as session:
				xid = await session.scalar(func.txid_current())
				try:
					cls.logger.debug("Transaction BEGIN;", extra={"xid": xid})
					yield session
					await session.commit()
					cls.logger.debug("Transaction COMMIT;", extra={"xid": xid})
				except Exception:
					await session.rollback()
					cls.logger.debug("Transaction ROLLBACK;", extra={"xid": xid})
					raise

		return _get_session


def AsyncSessionMaker(db_settings: DBSettings):  # noqa: N802
	return SQLAlchemyManager.get_async_session_generator(db_settings)


db = DBSettings(database_url=get_config().db.url)
get_session = AsyncSessionMaker(db)  # use as Depends(get_session)
# engine = SQLAlchemyManager.get_async_engine(db)
# sessionmaker = partial(SQLAlchemyManager.get_async_session, db)  # use as async with sessionmaker() as session:
