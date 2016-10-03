from swiftclient.client import ClientException as SwiftClientException


class SwiftNotFoundException(SwiftClientException):
    """Not found, 404"""
    pass


class SwiftNotAuthorized(SwiftClientException):
    """Not authorised, 401"""
    pass
