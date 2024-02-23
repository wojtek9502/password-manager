import logging

from fastapi import APIRouter, Depends

from src.api import auth
from src.api.tools.schema import HealthzSchema

router = APIRouter(tags=['Tools'])
logger = logging.getLogger()


@router.get("/healthz", status_code=200, response_model=HealthzSchema)
async def healthz():
    return {"status": "ok"}