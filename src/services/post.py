import json
from typing import List
from dataclasses import dataclass

from fastapi import HTTPException

from database.async_redis import CacheDB

from models.post import Post

from schemas import PostSchema, AddPostSchema

from repositories import PostRepository


@dataclass
class PostService:
	post_repo: PostRepository
	redis: CacheDB


	async def create_post(self, data: AddPostSchema, user_id: int) -> int:
		new_post = await self.post_repo.add(
			Post(
				user_id=user_id,
				text=data.text
			)
		)

		return new_post.id


	async def get_all_posts(self, user_id: int) -> List[PostSchema]:
		cache_key = f"user:{user_id}:posts"
		cached_posts = await self.redis.get(cache_key)

		if cached_posts:
			return [PostSchema(**post) for post in json.loads(cached_posts)]

		posts = await self.post_repo.find_all_by({"user_id": user_id})
		post_list = [PostSchema.from_orm(post) for post in posts]

		await self.redis.set(json.dumps([post.dict() for post in post_list]), cache_key, 300)

		return post_list


	async def delete_post(self, post_id: int):
		post = await self.post_repo.find_one(post_id)

		if not post:
			raise HTTPException(404, f'Post with id {post_id} not found')

		await self.post_repo.delete(post_id)

		return True
