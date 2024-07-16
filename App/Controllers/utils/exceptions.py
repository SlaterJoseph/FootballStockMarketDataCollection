class AuthorizationError(Exception):
    """
    A exception to be raised if a password check fails
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()

