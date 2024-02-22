import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api import auth
from src.api.user.schema import LoginResponseSchema, UserResponseSchema, UserUuidResponseSchema, LoginRequestSchema, \
    UserCreateRequestSchema, UserUpdateRequestSchema
from src.common.BaseRepository import NotFoundEntityError
from src.common.db_session import get_db_session
from src.user.exceptions import UserLoginPasswordInvalidError
from src.user.services import UserService, UserTokenService

router = APIRouter(prefix='/user', tags=['Users'])
logger = logging.getLogger()


@router.post("/login", response_model=LoginResponseSchema)
async def login(request: LoginRequestSchema, session: Session = Depends(get_db_session)):
    user_service = UserService(session=session)
    user_token_service = UserTokenService(session=session)

    try:
        user_logged_jwt_token = user_service.login_user(
            username=request.username,
            password_clear=request.password
        )
    except (NotFoundEntityError, UserLoginPasswordInvalidError):
        msg = "Invalid username or password"
        raise HTTPException(status_code=401, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    user_entity = user_service.find_by_username(username=request.username)
    if not user_entity:
        raise HTTPException(status_code=404, detail=f"Not found user {request.username}")

    entity = user_token_service.create_token(
        token=user_logged_jwt_token,
        user_id=user_entity.id
    )

    return LoginResponseSchema(
        token=entity.token
    )


@router.get("/", response_model=List[UserResponseSchema],
            dependencies=[Depends(auth.validate_api_key)])
async def find_all(session: Session = Depends(get_db_session)):
    service = UserService(session=session)

    try:
        entities = service.find_all()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    users_response: List[UserResponseSchema] = []
    for entity in entities:
        entity_data = UserResponseSchema(
            id=entity.id,
            username=entity.username,
        )
        users_response.append(entity_data)
    return users_response


@router.get("/by_username", response_model=UserResponseSchema,
            dependencies=[Depends(auth.validate_api_key)])
async def find_by_username(username: str, session: Session = Depends(get_db_session)):
    service = UserService(session=session)

    try:
        entity = service.find_by_username(
            username=username,
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"Not found user with username: '{username}'")

    return UserResponseSchema(
        id=entity.id,
        username=entity.username
    )


@router.post("/create", response_model=UserResponseSchema,
             dependencies=[Depends(auth.validate_api_key)])
async def create(request: UserCreateRequestSchema, session: Session = Depends(get_db_session)):
    service = UserService(session=session)

    try:
        entity = service.create_user(
            username=request.username,
            password_clear=request.password
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail="User create error")

    return UserResponseSchema(
        id=entity.id,
        username=entity.username
    )


@router.post("/update", response_model=UserResponseSchema,
             dependencies=[Depends(auth.validate_api_key)])
async def update(request: UserUpdateRequestSchema, session: Session = Depends(get_db_session)):
    service = UserService(session=session)
    try:
        entity = service.update_user(
            user_id=request.user_id,
            password_clear=request.password
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail="User update error")

    return UserResponseSchema(
        id=entity.id,
        username=entity.username
    )


@router.delete("/delete", response_model=UserUuidResponseSchema,
               dependencies=[Depends(auth.validate_api_key)])
async def delete(user_id: UUID, session: Session = Depends(get_db_session)):
    service = UserService(session=session)
    try:
        entity_id = service.delete_user(
            user_id=user_id,
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail="User delete error")

    return UserUuidResponseSchema(id=entity_id)
