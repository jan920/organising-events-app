from flask import Blueprint, jsonify
from ewentts.utils import requires_auth
import logging

main = Blueprint("main", __name__)
logger = logging.getLogger('main')


@main.route('/', methods=["GET", "POST"])
@requires_auth
def about():
    logger.info("main page called")
    response = 123
    return jsonify(response), 200


@main.route("/home", methods=["GET"])
@requires_auth
def home():
    return jsonify("home"), 200
