import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from src.api import auth
from src.api.password.parsers import parse_password_history_to_response_schema, \
    parse_password_history_entities_to_response_schema
from src.api.password.schema import PasswordListResponseSchema, PasswordCreateResponseSchema, \
    PasswordCreateRequestSchema, PasswordUpdateRequestSchema, PasswordUpdateResponseSchema, \
    PasswordDeleteResponseSchema, PasswordResponseSchema, PasswordGroupResponseSchema, PasswordUrlResponseSchema, \
    PasswordHistoryResponseSchema
from src.common.BaseRepository import NotFoundEntityError
from src.common.db_session import get_db_session
from src.common.db_utils import entity_to_dict
from src.password.exceptions import PasswordError
from src.password.services import PasswordService, PasswordHistoryService
from src.password.types import PasswordDTO
from src.user.exceptions import MasterTokenInvalidUseError
from src.user.services import UserService

router = APIRouter(prefix='/password', tags=['Passwords'])
logger = logging.getLogger()


@router.get("/list", dependencies=[Depends(auth.validate_api_key)], response_model=PasswordListResponseSchema)
async def password_list(request: Request, session: Session = Depends(get_db_session)):
    passwords_items = []
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)
    token = request.headers['X-API-KEY']

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    passwords_dtos = password_service.get_user_passwords_dtos(user_id=user_id)
    for password_dto in passwords_dtos:
        password_groups_entities = password_service.get_password_groups(password_id=password_dto.id)
        password_groups = [PasswordGroupResponseSchema.model_validate(entity_to_dict(group)) for group in password_groups_entities]
        password_urls = [PasswordUrlResponseSchema.model_validate(entity_to_dict(url)) for url in password_dto.urls]
        password_history_items = [parse_password_history_to_response_schema(history) for history in password_dto.history]

        password_item = PasswordResponseSchema(
            password_id=password_dto.id,
            name=password_dto.name,
            login=password_dto.login,
            password_encrypted=password_dto.password_encrypted.decode(),
            client_side_algo=password_dto.client_side_algo,
            client_side_iterations=password_dto.client_side_iterations,
            user_id=password_dto.user_id,
            urls=password_urls,
            history=password_history_items,
            groups=password_groups
        )
        passwords_items.append(password_item)
    return PasswordListResponseSchema(passwords=passwords_items)


@router.get("/{password_id}/history", dependencies=[Depends(auth.validate_api_key)],
            response_model=List[PasswordHistoryResponseSchema])
async def password_history_list(request: Request, password_id: uuid.UUID, session: Session = Depends(get_db_session)):
    user_service = UserService(session=session)
    password_history_service = PasswordHistoryService(session=session)
    token = request.headers['X-API-KEY']

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    try:
        password_history_dtos = password_history_service.get_password_history(
            password_id=password_id,
            user_id=user_id
        )
    except PasswordError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    return parse_password_history_entities_to_response_schema(password_history_dtos)

@router.post("/create",
             dependencies=[Depends(auth.validate_api_key)],
             response_model=PasswordCreateResponseSchema)
async def create(request: PasswordCreateRequestSchema,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    password_details: PasswordDTO = PasswordDTO(
        name=request.name,
        login=request.login,
        password_encrypted=request.password_encrypted.encode(),
        client_side_algo=request.client_side_algo,
        client_side_iterations=request.client_side_iterations,
        note=request.note,
        urls=request.urls,
        groups_ids=request.groups_ids,
        user_id=user_id
    )
    password = password_service.create(password_details)
    password_urls = [url.url for url in password.urls]
    groups_ids = [group.id for group in password.groups]

    return PasswordCreateResponseSchema(
        password_id=password.id,
        name=password.name,
        login=password.login,
        note=password.note,
        urls=password_urls,
        user_id=password.user_id,
        groups_ids=groups_ids
    )


@router.post("/update",
             dependencies=[Depends(auth.validate_api_key)],
             response_model=PasswordUpdateResponseSchema)
async def update(request: PasswordUpdateRequestSchema,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    password_details: PasswordDTO = PasswordDTO(
        name=request.name,
        login=request.login,
        password_encrypted=request.password_encrypted.encode(),
        client_side_algo=request.client_side_algo,
        client_side_iterations=request.client_side_iterations,
        note=request.note,
        urls=request.urls,
        groups_ids=request.groups_ids,
        user_id=user_id
    )
    password = password_service.update(
        entity_id=request.password_id,
        password_new_details=password_details
    )
    password_urls = [url.url for url in password.urls]
    groups_ids = [group.id for group in password.groups]
    return PasswordUpdateResponseSchema(
        password_id=password.id,
        name=password.name,
        login=password.login,
        note=password.note,
        urls=password_urls,
        user_id=password.user_id,
        groups_ids=groups_ids
    )


@router.delete("/delete",
               dependencies=[Depends(auth.validate_api_key)],
               response_model=PasswordDeleteResponseSchema)
async def delete(password_id: uuid.UUID,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    password_service = PasswordService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    try:
        deleted_password_id = password_service.delete(
            password_id=password_id,
            user_id=user_id
        )
    except NotFoundEntityError:
        logger.error(f"Not found password with id {password_id}")
        raise HTTPException(status_code=404, detail=f"Not found password with id {password_id}")

    return PasswordDeleteResponseSchema(
        password_id=deleted_password_id
    )