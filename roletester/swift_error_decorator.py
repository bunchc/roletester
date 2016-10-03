from swiftclient.client import ClientException as SwiftClientException
from swift_exceptions import SwiftNotAuthorized
from swift_exceptions import SwiftNotFoundException
from swift_exceptions import SwiftForbidden


def swift_error(swift_function):
    def wrapper(*args, **kwargs):
        try:

            result = swift_function(*args, **kwargs)
            return result
        except SwiftClientException as exception:
            if exception.http_status == 404:
                raise SwiftNotFoundException(exception)
            if exception.http_status == 401:
                raise SwiftNotAuthorized(exception)
            if exception.http_status == 403:
                raise SwiftForbidden(exception)
            else:
                raise

    return wrapper

