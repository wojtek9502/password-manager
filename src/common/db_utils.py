from typing import Dict


def entity_to_dict(entity) -> Dict:
    data = {}
    for column in entity.__table__.columns:
        if isinstance(getattr(entity, column.name), bytes):
            data[column.name] = getattr(entity, column.name).decode()
        else:
            data[column.name] = str(getattr(entity, column.name))
    return data
