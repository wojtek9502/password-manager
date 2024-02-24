class PasswordError(Exception):
    ...


class PasswordNotFoundError(PasswordError):
    ...


class PasswordNotBelongsToUserError(PasswordError):
    ...
