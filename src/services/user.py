import hashlib
from dataclasses import dataclass

from fastapi import HTTPException

from models.user import User

from schemas.user import LoginSchema, SignUpSchemas, UserSchema

from .authentication import create_access_token

from repositories import UserRepository


@dataclass
class UserService:
	user_repo: UserRepository


	async def login(self, data: LoginSchema) -> str:
		user = await self.user_repo.find_one_by(
			{
				"login": data.login
			}
		)

		if not user:
			raise HTTPException(404, 'User not found')

		password_sha = hashlib.sha256(data.password.encode()).hexdigest()

		if user.password_sha256 != password_sha:
			raise HTTPException(409, 'Password is wrong')

		token = await create_access_token(UserSchema.from_orm(User))

		return token


	async def sign_up(self, data: SignUpSchemas) -> str:
		existing_user = await self.user_repo.find_one_by(
			{
				'login': data.login
			}
		)

		if existing_user:
			raise HTTPException(409, 'User with this login was found')

		password_sha = hashlib.sha256(data.password.encode()).hexdigest()

		new_user = User(
			login=data.login,
			password_sha256=password_sha
		)

		await self.user_repo.add(new_user)

		token = await create_access_token(UserSchema.from_orm(User))

		return token
