import os

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

from src.common.db_session import SessionLocal
from src.user.services import UserTokenService

API_KEY_NAME = 'X-API-KEY'
API_KEY = os.environ['API_AUTH_MASTER_TOKEN']
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def _is_token_valid_with_main_token(api_key) -> bool:
    if api_key == API_KEY:
        return True
    return False


def _is_user_token_valid(api_key) -> bool:
    session = SessionLocal()
    user_token_service = UserTokenService(session=session)

    is_token_valid = user_token_service.is_token_valid(token=api_key)

    if session.is_active:
        session.close()

    return is_token_valid

async def validate_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail='Invalid or missing API Key')

    is_token_valid = _is_token_valid_with_main_token(api_key=api_key)
    if is_token_valid:
        return

    is_user_token_valid = _is_user_token_valid(api_key=api_key)
    if is_user_token_valid:
        return

    raise HTTPException(status_code=401, detail='Invalid or missing API Key')
