class TokenReceivingException(Exception):
    """Error receiving the token."""

    ...


class SendRequestException(Exception):
    """Error send request."""

    ...


class NotFoundEndpointException(KeyError):
    """Error find endpoint."""

    ...


class NotFoundDataException(Exception):
    """Error load data."""

    ...
