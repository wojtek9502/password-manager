import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from src.api import auth
from src.api.group.parsers import parse_group_to_response_schema
from src.api.group.schema import GroupResponseSchema, GroupCreateRequestSchema, GroupUpdateRequestSchema, \
    GroupDeleteResponseSchema
from src.common.BaseRepository import NotFoundEntityError
from src.common.db_session import get_db_session
from src.group.services import GroupService
from src.user.exceptions import MasterTokenInvalidUseError
from src.user.services import UserService

router = APIRouter(prefix='/group')
logger = logging.getLogger()


@router.get("/list", dependencies=[Depends(auth.validate_api_key)], response_model=List[GroupResponseSchema])
async def groups_list(request: Request, session: Session = Depends(get_db_session)):
    user_service = UserService(session=session)
    group_service = GroupService(session=session)
    token = request.headers['X-API-KEY']

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no group for this API token")
        raise HTTPException(status_code=404, detail="There is no group for this API token")

    groups_data = group_service.find_user_groups(user_id=user_id)
    parsed_groups_data = [parse_group_to_response_schema(group) for group in groups_data]

    return parsed_groups_data


@router.post("/create",
             dependencies=[Depends(auth.validate_api_key)],
             response_model=GroupResponseSchema)
async def create(request: GroupCreateRequestSchema,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    group_service = GroupService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no group for this API token")
        raise HTTPException(status_code=404, detail="There is no group for this API token")

    group = group_service.create_group_with_user(name=request.name, user_id=user_id)

    return GroupResponseSchema(
        group_id=group.id,
        name=group.name,
    )


@router.post("/update",
             dependencies=[Depends(auth.validate_api_key)],
             response_model=GroupResponseSchema)
async def update(request: GroupUpdateRequestSchema,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    group_service = GroupService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no group for this API token")
        raise HTTPException(status_code=404, detail="There is no group for this API token")

    group = group_service.update(
        group_id=request.group_id,
        new_name=request.name,
        user_id=user_id
    )

    return GroupResponseSchema(
        group_id=group.id,
        name=group.name,
    )


@router.delete("/delete",
               dependencies=[Depends(auth.validate_api_key)],
               response_model=GroupDeleteResponseSchema)
async def delete(group_id: uuid.UUID,
                 session: Session = Depends(get_db_session),
                 x_api_key: Annotated[str | None, Header(include_in_schema=False)] = None):
    token = x_api_key
    user_service = UserService(session=session)
    group_service = GroupService(session=session)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no passwords for this API token")
        raise HTTPException(status_code=404, detail="There is no passwords for this API token")

    try:
        deleted_group_id = group_service.delete(
            group_id=group_id,
            user_id=user_id
        )
    except NotFoundEntityError:
        logger.error(f"Not found group with id {group_id}")
        raise HTTPException(status_code=404, detail=f"Not found group with id {group_id}")

    return GroupDeleteResponseSchema(
        group_id=deleted_group_id
    )
