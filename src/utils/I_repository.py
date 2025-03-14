from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc, func
from sqlalchemy.orm import joinedload
from collections.abc import Iterable
from typing import Any, TypeAlias

from sqlalchemy.engine import Result
from sqlalchemy.sql import Select


from typing import Generic, TypeVar, Type, List, Optional, Callable
from abc import ABC, abstractmethod

T = TypeVar("T")
ModelType = TypeVar("ModelType")
Statement: TypeAlias = Any


class IRepository(ABC, Generic[T]):
	@abstractmethod
	async def find_one(self, entity_id: int) -> Optional[T]:
		pass

	@abstractmethod
	async def find_all(self) -> List[T]:
		pass

	@abstractmethod
	async def upd(self, entity_id: int, **kwargs) -> Optional[T]:
		pass

	@abstractmethod
	async def delete(self, entity_id: int) -> bool:
		pass

	@abstractmethod
	async def add(self, obj_in: T) -> T:
		pass

	@abstractmethod
	async def find_one_by(
		self,
		filters: dict[str, any],
		join_models: Optional[list[Callable]] = None,
	) -> Optional[T]:
		pass

	@abstractmethod
	async def find_all_by(
		self,
		filters: dict[str, any],
		join_models: Optional[list[Callable]] = None,
		order_by: Optional[Callable] = None,
		limit: Optional[int] = None,
		offset: Optional[int] = None
	) -> List[T]:
		pass

	@abstractmethod
	async def count_by(
		self,
		filters: dict = {},
		group_by: Optional[list[str]] = None
	) -> int:
		pass


class BaseRepository(IRepository[T], Generic[T]):
	def __init__(self, db_session: AsyncSession, model: Type[T]):
		self.db_session = db_session
		self.model = model

	async def find_one(self, entity_id: int) -> Optional[T]:
		stmt = select(self.model).where(self.model.id == entity_id)
		result = await self.db_session.execute(stmt)
		return result.scalar_one_or_none()

	async def find_all(
		self,
		order_by: Optional[dict[str, str]] = None,
		limit: Optional[int] = None,
		offset: Optional[int] = None
	) -> List[T]:
		stmt = select(self.model)

		if order_by:
			order_conditions = []
			for field, direction in order_by.items():
				column = getattr(self.model, field)
				if direction == 'desc':
					order_conditions.append(desc(column))
				else:
					order_conditions.append(asc(column))
			stmt = stmt.order_by(*order_conditions)

		if limit is not None:
			stmt = stmt.limit(limit)

		if offset is not None:
			stmt = stmt.offset(offset)

		result = await self.db_session.execute(stmt)
		return result.scalars().all()

	async def upd(self, entity_id: int, **kwargs) -> Optional[T]:
		obj = await self.find_one(entity_id)
		if obj:
			for key, value in kwargs.items():
				setattr(obj, key, value)
			await self.db_session.commit()
			await self.db_session.refresh(obj)
		return obj

	async def delete(self, entity_id: int) -> bool:
		obj = await self.find_one(entity_id)
		if obj:
			await self.db_session.delete(obj)
			await self.db_session.commit()
			return True
		return False

	async def add(self, obj_in: T) -> T:
		self.db_session.add(obj_in)
		await self.db_session.commit()
		await self.db_session.refresh(obj_in)
		return obj_in

	async def find_one_by(
		self,
		filters: dict[str, any],
		join_models: Optional[list[Callable]] = None,
	) -> Optional[T]:
		stmt = select(self.model)

		filter_conditions = []
		for field, value in filters.items():
			parts = field.split('.')

			if len(parts) > 1:
				related_model_name = parts[0]
				column_name = parts[1]

				join_model_list = []
				for model in join_models:
					if model.__name__.lower() == related_model_name.lower():
						join_model_list.append(model)
						break

				for join_model in join_model_list:
					stmt = stmt.join(join_model)

					column = getattr(join_model, column_name)
					filter_conditions.append(column == value)
			else:
				column = getattr(self.model, parts[0], None)
				if column:
					filter_conditions.append(column == value)

		stmt = stmt.where(and_(*filter_conditions))

		result = await self.db_session.execute(stmt)
		return result.scalar_one_or_none()

	async def find_all_by(
		self,
		filters: dict[str, any],
		join_models: Optional[list[Callable]] = None,
		order_by: Optional[dict[str, str]] = None,
		limit: Optional[int] = None,
		offset: Optional[int] = None,
		group_by: Optional[list[str]] = None,
		eager_load: Optional[List[str]] = None
	) -> List[T]:
		stmt = select(self.model)

		if join_models:
			for join_model in join_models:
				stmt = stmt.join(join_model)

		filter_conditions = []
		for field, value in filters.items():
			parts = field.split('.')

			if len(parts) > 1:
				related_model_name = parts[0]
				column_name = parts[1]

				join_model_list = List[None]
				for model in join_models:
					if model.__name__.lower() == related_model_name.lower():
						join_model_list.append(model)
						break

				for join_model in join_model_list:
					stmt = stmt.join(join_model)

					column = getattr(join_model, column_name)
					filter_conditions.append(column == value)
			else:
				column = getattr(self.model, parts[0], None)
				if column:
					filter_conditions.append(column == value)

		if 'timestamp' in filters:
			start_date, end_date = filters['timestamp']
			stmt = stmt.where(self.model.timestamp >= start_date, self.model.timestamp <= end_date)

		stmt = stmt.where(and_(*filter_conditions))

		if eager_load:
			for relation in eager_load:
				stmt = stmt.options(joinedload(getattr(self.model, relation)))

		if group_by:
			stmt = stmt.group_by(column)

		if order_by:
			order_conditions = []
			for field, direction in order_by.items():
				column = getattr(self.model, field)
				if direction == 'desc':
					order_conditions.append(desc(column))
				else:
					order_conditions.append(asc(column))
			stmt = stmt.order_by(*order_conditions)

		if limit is not None:
			stmt = stmt.limit(limit)

		if offset is not None:
			stmt = stmt.offset(offset)

		result = await self.db_session.execute(stmt)
		return result.scalars().all()

	async def count_by(
		self,
		filters: dict = {},
		group_by: Optional[list[str]] = None,
	) -> int:
		stmt = select(func.count()).select_from(self.model)

		if filters:
			for key, value in filters.items():
				column = getattr(self.model, key)
				if isinstance(value, dict):
					for op, op_value in value.items():
						if op == '$gt':
							stmt = stmt.filter(column > op_value)
						elif op == '$lt':
							stmt = stmt.filter(column < op_value)
				else:
					stmt = stmt.filter(column == value)


		if group_by:
			for key in group_by:
				stmt = stmt.group_by(getattr(self.model, key))

		result = await self.db_session.execute(stmt)
		return result.scalar()


class AsyncSessionUtil:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def execute(self, stmt: Statement, **kwargs: Any) -> Result:
		return await self.session.execute(stmt, **kwargs)

	async def one(self, stmt: Select[ModelType]) -> ModelType | None:
		return (await self.execute(stmt)).scalars().one_or_none()

	async def all(self, stmt: Select) -> list[ModelType]:
		return (await self.session.execute(stmt)).scalars().all()

	def add(self, obj: ModelType) -> None:
		self.session.add(obj)

	def add_batch(self, obj_list: list[ModelType]) -> None:
		self.session.add_all(obj_list)

	async def delete(self, obj: ModelType) -> None:
		await self.session.delete(obj)

	async def refresh(self, obj: ModelType, attrs: Iterable[str]) -> None:
		await self.session.refresh(obj, attrs)

	async def flush(self, objs: Iterable[ModelType] | None = None) -> None:
		await self.session.flush(objs)

	async def save(self, obj: ModelType) -> ModelType:
		self.session.add(obj)
		await self.session.flush()
		await self.session.refresh(obj)
		return obj

	async def batch_save(self, objs: list[ModelType]) -> None:
		self.add_batch(objs)
		await self.session.flush()

	async def _commit(self) -> None:
		await self.session.commit()
