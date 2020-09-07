from typing import Dict


class UpBankException(Exception):
    """
    Base class for all Up specific exceptions,
    this will not cover all possible exceptions such as network or JSON decoding errors.
    """

    def __init__(self, error):
        super().__init__()
        self.__status = error.get("status")
        self.__title = error.get("title")
        self.__detail = error.get("detail")
        self.__source = error.get("source")
        self.args = (self.status, self.title, self.detail)

    @property
    def status(self) -> str:
        """
        The status returned by the Up API
        """
        return self.__status

    @property
    def title(self) -> str:
        """
        Title of the error
        """
        return self.__title

    @property
    def detail(self) -> str:
        """
        Detailed description of the error
        """
        return self.__detail

    @property
    def source(self) -> Dict:
        """
        Source of the error
        """
        return self.__source

    def __str__(self):
        return "({status}) {title}: {detail}".format(
            status=self.status, title=self.title, detail=self.detail
        )


class NotAuthorizedException(UpBankException):
    """Raised for an invalid Up token."""


class RateLimitExceededException(UpBankException):
    """Raised when too many requests are made to the API."""


class BadResponseException(UpBankException):
    """Raised when a response from the API is not formatted correctly."""
