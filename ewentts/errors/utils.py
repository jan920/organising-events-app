"""Module containing functions used by handlers.py module"""

from flask import jsonify, make_response


def get_error_message(error, code, title):
    """Extract and return error message from error if
    present if not create new error message"""
    try:
        error_message = error.description
    except AttributeError:
        error_message = {
            "error_message": error.message,
            "source_function": None,
            "source_file": None,
            "code": code,
            "title": title
        }
    return error_message


def create_response(error, code, title):
    """Create error response"""
    error_message = get_error_message(error, code, title)
    json = {"error": error_message}
    json = jsonify(json)
    response = make_response(json)
    response.status_code = code
    return response
