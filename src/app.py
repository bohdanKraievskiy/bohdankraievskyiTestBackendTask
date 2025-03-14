import datetime
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.user import router as user_router
from routes.post import router as post_router

from routes.sync import router as sync_router

from config import ENVIRONMENT


logging.basicConfig(
	filename='app_{:%Y-%m-%d}.log'.format(datetime.datetime.now()),
	format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
	level=logging.INFO,
)

app = FastAPI(
	docs_url="/swagger-docs",
	openapi_prefix='/stats' if ENVIRONMENT == 'production' else '/dev',
	swagger_ui_parameters={
		"persistAuthorization": "true",
	}
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(post_router, prefix="/post", tags=["Post"])
