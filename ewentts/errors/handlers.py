"""Module for error handling and returning other status codes then 2xx

Module for handling following status codes:
400, 403, 404, 405, 500

"""

from flask import Blueprint
from .utils import create_response

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(400)
def error_400(error):
    """Bad Request error handler

    :param error: contains:
                        detail: detail error message
                        error_message: error message
                        source: location where error happened
                        code: error status code
                        title: error title
    :return: Response with error in body and 400 status code
    """
    title = "Bad Request"
    response = create_response(error, 400, title)
    return response


@errors.app_errorhandler(403)
def error_403(error):
    """Forbidden error handler

    :param error: contains:
                        detail: detail error message
                        error_message: error message
                        source: location where error happened
                        code: error status code
                        title: error title
    :return: Response with error in body and 403 status code
    """
    title = "Forbidden"
    response = create_response(error, 403, title)
    return response


@errors.app_errorhandler(404)
def error_404(error):
    """Not Found error handler

    :param error: contains:
                        detail: detail error message
                        error_message: error message
                        source: location where error happened
                        code: error status code
                        title: error title
    :return: Response with error in body and 404 status code
    """

    title = "Not Found"
    response = create_response(error, 404, title)
    return response


@errors.app_errorhandler(405)
def error_405(error):
    """Method Not Allowed error handler

    :param error: contains:
                        detail: detail error message
                        error_message: error message
                        source: location where error happened
                        code: error status code
                        title: error title
    :return: Response with error in body and 405 status code
    """
    title = "Method Not Allowed"
    response = create_response(error, 405, title)
    return response


@errors.app_errorhandler(500)
def error_500(error):
    """Server error handler

    :param error: contains:
                        detail: detail error message
                        error_message: error message
                        code: error status code
                        title: error title
    :return: Response with error in body and 500 status code
    """
    title = "Server Error"
    response = create_response(error, 500, title)
    return response
