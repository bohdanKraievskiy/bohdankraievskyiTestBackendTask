import json
import logging

from typing import Any
from datetime import timedelta

from redis.asyncio import ConnectionPool, Redis

from pydantic.json import pydantic_encoder

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, ENVIRONMENT, get_config


def connection_pool_generator():
	pool = ConnectionPool(
		host=REDIS_HOST,
		port=REDIS_PORT,
		password=REDIS_PASSWORD if ENVIRONMENT == 'production' else None,
		ssl=True if ENVIRONMENT == 'production' else False,
		decode_responses=True,
	)
	while True:
		yield pool


class CacheDB:
	def __init__(self):
		self.config = get_config()
		self.redis = Redis(
			host=self.config.redis.host,
			port=self.config.redis.port,
			password=self.config.redis.password if self.config.general.environment == 'production' else None,
			ssl=True if self.config.general.environment == 'production' else False,
			decode_responses=True,
			encoding="utf-8",
		)
		self.log = logging.getLogger(self.__class__.__name__)

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.redis.close()

	def pipeline(self):
		return self.redis.pipeline()

	async def incr(self, name: Any, amount: int = 1):
		return await self.redis.incr(name=name, amount=amount)

	async def expire(self, name: Any, time: int | timedelta):
		await self.redis.expire(name=name, time=time)

	async def set(self, name: Any, value: Any, expire_time: int | timedelta):
		await self.redis.set(name=name, value=value, ex=expire_time)

	async def get(self, name: Any) -> Any:
		return await self.redis.get(name=name)

	async def delete(self, names: Any) -> Any:
		return await self.redis.delete(names)

	async def set_cache(
		self,
		data: dict,
		key: str,
		expiration: int | None = 3600,
	):
		data_str = json.dumps(data, default=pydantic_encoder)
		await self.redis.set(key, data_str, expiration)

	async def persist(self, k: str, value: Any, to_json: bool = True, expire_time: int | timedelta | None = None):
		if to_json:
			val = json.dumps(value, default=pydantic_encoder)
		else:
			val = value
		await self.set(name=k, value=val, expire_time=expire_time)
