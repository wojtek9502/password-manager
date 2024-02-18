import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session

from src.api import auth
from src.api.auth import API_KEY_NAME
from src.api.password.schema import PasswordListResponseSchema, PasswordCreateResponseSchema, \
    PasswordCreateRequestSchema
from src.common.db_session import get_db_session
from src.password.services import PasswordService
from src.password.types import PasswordDTO
from src.user.exceptions import MasterTokenInvalidUseError
from src.user.services import UserService

router = APIRouter(prefix='/password')
logger = logging.getLogger()


@router.get("/list", dependencies=[Depends(auth.validate_api_key)], response_model=PasswordListResponseSchema)
async def password_list(session: Session = Depends(get_db_session),
                        x_api_key: Annotated[str | None, Header()] = None):
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)
    token = x_api_key

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no password connected with master API token")
        return {}

    passwords = password_service.find_all_by_user(user_id=user_id)
    return passwords


@router.post("/create",
             dependencies=[Depends(auth.validate_api_key)],
             response_model=PasswordCreateResponseSchema)
async def create(request: PasswordCreateRequestSchema,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header()] = None):
    token = x_api_key
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no password connected with master API token")
        return {}

    password_details: PasswordDTO = PasswordDTO(
        name=request.name,
        login=request.login,
        client_side_password_encrypted=request.password_encrypted.encode(),
        client_side_algo=request.client_side_algo,
        client_side_iterations=request.client_side_iterations,
        note=request.note,
        urls=request.urls,
        groups_ids=request.groups_ids,
        user_id=user_id
    )
    password = password_service.create(password_details)
    password_urls = [url.url for url in password.urls]
    return PasswordCreateResponseSchema(
        name=password.name,
        login=password.name,
        note=password.note,
        urls=password_urls,
        user_id=password.user_id,
        groups_ids=[]
    )


# TODO add request schema in decorator and return schema
@router.post("/update",
             dependencies=[Depends(auth.validate_api_key)])
async def update(request):
    ...


# TODO add request schema in decorator and return schema
@router.delete("/delete",
               dependencies=[Depends(auth.validate_api_key)])
async def delete(user_id: UUID):
    ...