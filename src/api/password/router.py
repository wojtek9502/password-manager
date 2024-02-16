import logging
import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api import auth
from src.api.auth import API_KEY_NAME
from src.password.services import PasswordService
from src.user.exceptions import MasterTokenInvalidUseError
from src.user.services import UserService

router = APIRouter(prefix='/password')
logger = logging.getLogger()

# TODO add request schema in decorator and return schema
@router.get("/list", dependencies=[Depends(auth.validate_api_key)])
async def password_list(request: Request):
    user_service = UserService()
    password_service = PasswordService()
    token = request.headers.get(API_KEY_NAME)

    try:
        user_id = user_service.find_id_by_token(token=token)
    except MasterTokenInvalidUseError:
        logger.warning("There is no password connected with master API token")
        return {}

    passwords = password_service.find_all_by_user(user_id=user_id)
    return passwords


# TODO add request schema in decorator and return schema
@router.post("/create",
             dependencies=[Depends(auth.validate_api_key)])
async def create(request):
    ...


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