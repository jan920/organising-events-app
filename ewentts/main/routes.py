"""Module for handling requests on / and /home endpoints

This module currently has no function and is only used for development


Attributes:
    main: flask Blueprint for calling main endpoints
    logger: Logger for logging in main module

"""
import logging

from flask import Blueprint, jsonify

from ewentts.utils import requires_auth

main = Blueprint("main", __name__)
logger = logging.getLogger('main')


@main.route('/', methods=["GET", "POST"])
@requires_auth
def about():
    """About Endpoint"""
    logger.info("main page called")
    response = "About"
    return jsonify(response), 200


@main.route("/home", methods=["GET"])
@requires_auth
def home():
    """Home Endpoint"""
    return jsonify("Home"), 200
