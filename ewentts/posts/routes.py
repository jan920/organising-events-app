from flask import request, Blueprint

from ewentts.utils import requires_auth, return_event
from utils import create_post, jsonify_post

posts = Blueprint("posts", __name__)


@posts.route("/event/<int:event_id>/post", methods=["POST"])
@requires_auth
def add_post(event_id):
    """Endpoint for creating posts.

    Properties:
        event_id: id of event where post is to be added
        content: string in json body

    Returns:
        201: properties of event in json
        400: if content is not provided in json body
        404: if event where post is to be added does not exist
        405: if other method then POST used
    """
    event = return_event(event_id)
    posts_num = len(event.posts)
    body = request.get_json()
    post = create_post(body, posts_num)
    json = jsonify_post(post, event)
    return json, 201
