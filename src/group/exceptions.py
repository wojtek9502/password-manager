class GroupError(Exception):
    ...


class GroupDeleteNotAllowedError(GroupError):
    ...


class GroupActionAuthError(GroupError):
    ...
