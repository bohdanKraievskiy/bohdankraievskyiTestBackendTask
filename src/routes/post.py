from typing import List
from fastapi import APIRouter, Depends

from dependencies import get_post_service

from schemas import AddPostSchema, DeletePostSchema, PostSchema

from services import PostService, Authentication

from schemas import ApiResult


router = APIRouter()


@router.post("/add")
async def create_post(
    current_user: Authentication,
    data: AddPostSchema,
    service: PostService = Depends(get_post_service)
) -> ApiResult[int]:
    post_id = await service.create_post(data, current_user.id)
    return ApiResult(success=True, message="Post was created", data=post_id)


@router.get("/all")
async def get_all_posts(
    current_user: Authentication,
    service: PostService = Depends(get_post_service)
) -> ApiResult[List[PostSchema]]:
    token = await service.get_all_posts(current_user.id)
    return ApiResult(success=True, message="All posts was retreived", data=token)


@router.delete("")
async def delete_post(
    _: Authentication,
    data: DeletePostSchema,
    service: PostService = Depends(get_post_service)
) -> ApiResult[bool]:
    success = await service.delete_post(data.post_id)
    return ApiResult(success=True, message="Post was deleted", data=success)
