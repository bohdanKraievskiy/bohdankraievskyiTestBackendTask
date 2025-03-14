from typing import List
from pydantic import BaseModel, Field

from config import MAX_POST_SIZE


class AddPostSchema(BaseModel):
    text: str = Field(..., max_length=MAX_POST_SIZE)


class PostSchema(BaseModel):
    id: int
    text: str


class GetPostsSchema(BaseModel):
    posts: List[PostSchema]


class DeletePostSchema(BaseModel):
    post_id: int
