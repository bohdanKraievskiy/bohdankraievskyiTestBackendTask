from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

RSP = TypeVar("RSP")

from .user import *
from .post import *


class ApiResult(BaseModel, Generic[RSP]):
	success: bool
	message: Optional[str] = None
	data: Optional[RSP] = None
