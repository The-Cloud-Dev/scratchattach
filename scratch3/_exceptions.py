class Unauthorized(Exception):
    pass

class Unauthenticated(Exception):
    pass

class UserNotFound(Exception):
    pass

class ProjectNotFound(Exception):
    pass

class ConnectionError(Exception):
    pass

class XTokenError(Exception):
    """
    Raised when there are no XToken headers available
    """
    pass

class LoginFailure(Exception):
    """
    Raised when there are no XToken headers available
    """
    pass

class InvalidCloudValue(Exception):
    pass

class FetchError(Exception):
    pass
