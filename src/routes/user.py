from fastapi import APIRouter, Depends

from dependencies import get_user_service

from schemas import LoginSchema, SignUpSchemas

from services import UserService, Authentication

from schemas import ApiResult


router = APIRouter()


@router.post("/login")
async def login(
    data: LoginSchema,
    service: UserService = Depends(get_user_service)
) -> ApiResult[str]:
    token = await service.login(data)
    return ApiResult(success=True, message="Login was success", data=token)


@router.post("/sign-up")
async def sign_up(
    data: SignUpSchemas,
    service: UserService = Depends(get_user_service)
) -> ApiResult[str]:
    token = await service.sign_up(data)
    return ApiResult(success=True, message="Sign up was success", data=token)
