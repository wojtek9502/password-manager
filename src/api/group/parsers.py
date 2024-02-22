from src.api.group.schema import GroupResponseSchema
from src.group.types import GroupDTO


def parse_group_to_response_schema(group_entity: GroupDTO) -> GroupResponseSchema:
    group_data = GroupResponseSchema(
        group_id=group_entity.id,
        name=group_entity.name
    )
    return group_data
