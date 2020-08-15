class UpBankException(Exception):
    """Base class for all up specific exceptions, this will not cover all possible exceptions such as network errors."""

    pass


class NotAuthorizedException(UpBankException):
    pass


class RateLimitExceededException(UpBankException):
    pass


class BadResponseException(UpBankException):
    pass
