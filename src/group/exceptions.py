class GroupError(Exception):
    ...


class GroupUpdateNotAllowedError(GroupError):
    ...


class GroupDeleteNotAllowedError(GroupError):
    ...
