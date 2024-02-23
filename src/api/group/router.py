import logging
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.api import auth
from src.api.auth import validate_is_master_key_used
from src.api.group.parsers import parse_group_to_response_schema
from src.api.group.schema import GroupResponseSchema, GroupCreateRequestSchema, GroupUpdateRequestSchema, \
    GroupDeleteResponseSchema
from src.common.db_session import get_db_session
from src.group.exceptions import GroupDeleteNotAllowedError
from src.group.services import GroupService
from src.user.services import UserService

router = APIRouter(prefix='/group', tags=['Groups'])
logger = logging.getLogger()


@router.get("/list",
            dependencies=[Depends(auth.validate_api_key)],
            response_model=List[GroupResponseSchema])
async def groups_list(request: Request, session: Session = Depends(get_db_session)):
    user_service = UserService(session=session)
    group_service = GroupService(session=session)
    token = request.headers['X-API-KEY']
    validate_is_master_key_used(api_key=token)

    user_id = user_service.find_id_by_token(token=token)
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
    validate_is_master_key_used(api_key=token)

    user_id = user_service.find_id_by_token(token=token)
    try:
        group = group_service.create_group_with_user(name=request.name, user_id=user_id)
    except SQLAlchemyError as e:
        logger.error(f"Create error {request.group_id}. Error {str(e)}")
        raise HTTPException(status_code=400, detail=f"Create error {request.group_id}. Error {str(e)}")

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
    validate_is_master_key_used(api_key=token)
    user_id = user_service.find_id_by_token(token=token)

    try:
        group = group_service.update(
            group_id=request.group_id,
            new_name=request.name,
            user_id=user_id
        )
    except SQLAlchemyError as e:
        logger.error(f"Update error group_id {request.group_id}. Error {str(e)}")
        raise HTTPException(status_code=400, detail=f"Update error group_id {request.group_id}. Error {str(e)}")

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
    user_id = user_service.find_id_by_token(token=token)

    try:
        deleted_group_id = group_service.delete(
            group_id=group_id,
            user_id=user_id
        )

    except (SQLAlchemyError, GroupDeleteNotAllowedError) as e:
        logger.error(f"Delete error {group_id}. Error {str(e)}")
        raise HTTPException(status_code=400, detail=f"Delete error {group_id}. Error {str(e)}")

    return GroupDeleteResponseSchema(
        group_id=deleted_group_id
    )
