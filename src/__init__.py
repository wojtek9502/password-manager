import logging
import os
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import create_engine
from dotenv import load_dotenv
from starlette.responses import RedirectResponse



PROJECT_DIR = Path(__file__).parent
LOGS_DIR = Path(PROJECT_DIR, 'logs')
logger = logging.getLogger()

load_dotenv()


# DB
from src.common.Database import Database
from src.user.models import UserModel, UserTokenModel, UserGroupModel
from src.group.models import GroupModel
from src.password.models import PasswordModel, PasswordUrlModel, PasswordHistoryModel, PasswordGroupModel

engine = create_engine(os.environ['DB_URI'])
Base = Database

# FastAPI
app = FastAPI(
    docs_url=f'/swagger-ui',
    redoc_url=f'/redoc',
    openapi_url=f'/openapi.json',
    dependencies=[],
)


@app.get("/", include_in_schema=False)
async def redirect_to_swagger():
    return RedirectResponse(url='/swagger-ui')


from src.api.user.router import router as user_router
from src.api.tools.router import router as tools_router
from src.api.password.router import router as password_router
from src.api.group.router import router as group_router

app.include_router(user_router)
app.include_router(password_router)
app.include_router(group_router)
app.include_router(tools_router)

