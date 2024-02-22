from src.api.password.schema import PasswordHistoryResponseSchema
from src.password.types import PasswordHistoryDTO


def parse_password_history_to_response_schema(password_history_entity: PasswordHistoryDTO) -> PasswordHistoryResponseSchema:
    password_history_data = PasswordHistoryResponseSchema(
        id=password_history_entity.id,
        name=password_history_entity.name,
        login=password_history_entity.login,
        password_encrypted=password_history_entity.client_side_password_encrypted,
        client_side_algo=password_history_entity.client_side_algo,
        client_side_iterations=password_history_entity.client_side_iterations,
        note=password_history_entity.note,
        user_id=password_history_entity.user_id,
        password_id=password_history_entity.id
    )
    return password_history_data
