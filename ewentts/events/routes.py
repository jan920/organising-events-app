"""Module for handling requests on /event endpoints

Attributes:
    events: flask Blueprint for calling generator endpoints

"""

from flask import Blueprint, jsonify

from ewentts.utils import requires_auth, request_uid, return_jsonified_users,\
    get_body_in_json, return_event, get_per_page, paginate_list, check_user_authorised
from .utils import create_event, jsonify_event, return_edited_event, logger,\
    return_jsonified_posts, invite_users, user_attends_event, user_came_to_event,\
    user_left_event

events = Blueprint("events", __name__)


@events.route('/event', methods=["POST"])
@requires_auth
def set_up_event():
    """
    Endpoint for creating events.

    If called with body containing valid:
     event_name: string
     start_datetime: iso datetime with location
     end_datetime: iso datetime with location
     location: list with 2 floats
     event_picture_url: picture url string, optional
     description: string, optional
     private: boolean
     guest_list: optional, list user_id of users

    Returns:
        201: properties of event in json
        400: if not all necessary parameters are provided in json body or if any of them is not valid
        405: if other method then POST used
    """
    body = get_body_in_json()
    user_id = request_uid()
    event = create_event(body, user_id)
    json = jsonify_event(event)
    return json, 201


@events.route("/event/<int:event_id>", methods=["GET"])
@requires_auth
def view_event(event_id):
    """Endpoint which returns event properties

    Properties:
        event_id: id of event which is to be viewed

    Returns:
        200: properties of event in json
        404: if event not found
        405: if other method then GET used
    """
    event = return_event(event_id)
    json = jsonify_event(event)
    return json, 200


@events.route("/event/<int:event_id>", methods=["DELETE"])
@requires_auth
def delete_event(event_id):
    """Endpoint which deletes event

    Properties:
        event_id: id of event which is to be deleted

    Returns:
        200: message that event was deleted in json
        403: if some other user then event organiser tried to delete the event
        404: if event not found
        405: if other method then DELETE used
    """
    event = return_event(event_id)
    current_user_id = request_uid()
    if check_user_authorised(current_user=current_user_id, authorised_user=event.organiser.id):
        event.key.delete()
        logger.info("Event {} Deleted".format(event_id))
    json = jsonify("Event Deleted")
    return json, 200


@events.route("/event/<int:event_id>/edit", methods=["POST"])
@requires_auth
def edit_event(event_id):
    """Endpoint which edits event

    These properties can get edited if valid values received in json body:
     event_name: string, optional
     start_datetime: iso datetime with location, optional
     end_datetime: iso datetime with location, optional
     event_picture_url: picture url string, optional
     description: string, optional

    Properties:
        event_id: id of event which is to be edited

    Returns:
        200: properties of event in json
        400: if any of the properties in body are not valid
        403: if some other user then event organiser tried to edit the event
        404: if event not found
        405: if other method then POST used
    """
    event = return_event(event_id)
    current_user_id = request_uid()
    if check_user_authorised(current_user=current_user_id, authorised_user=event.organiser.id):
        logger.info("user has right to edit")
        body = get_body_in_json()
        event = return_edited_event(event, body)
        json = jsonify_event(event)
        return json, 200


@events.route("/event/<int:event_id>/invite", methods=["POST"])
@requires_auth
def invite(event_id):
    """Endpoint which invites users to the event

    Properties:
        event_id: id of event where users are to be invited
        guest_list: in json body containing list of user_id


    Returns:
        200: properties of event in json
        400: if guest_list is not present in body
        403: if some other user then current user tried to edit the event
        404: if event not found
        405: if other method then POST used
    """
    event = return_event(event_id)
    current_user_id = request_uid()
    if check_user_authorised(current_user=current_user_id, authorised_user=event.organiser.id):
        body = get_body_in_json()
        event = invite_users(event, body)
        json = jsonify_event(event)
        return json, 200


@events.route("/event/<int:event_id>/attend", methods=["POST"])
@requires_auth
def attend_event(event_id):
    """Endpoint which adds user to attendees for the event

    Properties:
        event_id: id of event which user is to attend

    Returns:
        200: properties of event in json
        404: if event not found
        405: if other method then POST used
    """
    event = return_event(event_id)
    event = user_attends_event(event)
    json = jsonify_event(event)
    return json, 200


@events.route("/event/<int:event_id>/came", methods=["POST"])
@requires_auth
def came_to_event(event_id):
    """Endpoint which adds user to showed_up list for the event

    Properties:
        event_id: id of event where user came

    Returns:
        200: properties of event in json
        404: if event not found
        405: if other method then POST used
    """
    event = return_event(event_id)
    event = user_came_to_event(event)
    json = jsonify_event(event)
    return json, 200


@events.route("/event/<int:event_id>/left", methods=["POST"])
@requires_auth
def left_event(event_id):
    """Endpoint which adds user to left list for the event

    Properties:
        event_id: id of event from where user left

    Returns:
        200: properties of event in json
        404: if event not found
        405: if other method then POST used
    """
    event = return_event(event_id)
    event = user_left_event(event)
    json = jsonify_event(event)
    return json, 200


@events.route("/event/<int:event_id>/guest_list", methods=["GET"])
@requires_auth
def return_guest_list(event_id):
    """Endpoint which returns all users on the guest list

    Properties:
        event_id: id of event

    Returns:
        200: users, next_page and list_len in json
        404: if event not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    event = return_event(event_id)
    guest_list = event.guest_list
    guest_list_len = len(guest_list)
    if guest_list_len == 0:
        return jsonify(""), 204
    users_list, next_page = paginate_list(guest_list, per_page)
    json = return_jsonified_users(users_list, guest_list_len, next_page)
    return json, 200


@events.route("/event/<int:event_id>/attendees", methods=["GET"])
@requires_auth
def return_attendees(event_id):
    """Endpoint which returns all attendees

    Properties:
        event_id: id of event

    Returns:
        200: users, next_page and list_len in json
        404: if event not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    event = return_event(event_id)
    attendees = event.attendees
    attendees_len = len(attendees)
    if attendees_len == 0:
        return jsonify(""), 204
    users_list, next_page = paginate_list(attendees, per_page)
    json = return_jsonified_users(users_list, attendees_len, next_page)
    return json, 200


@events.route("/event/<int:event_id>/showed_up", methods=["GET"])
@requires_auth
def return_showed_up(event_id):
    """Endpoint which returns all users on showed_up list

    Properties:
        event_id: id of event

    Returns:
        200: users, next_page and list_len in json
        404: if event not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    event = return_event(event_id)
    showed_up = event.showed_up
    showed_up_len = len(showed_up)
    if showed_up_len == 0:
        return jsonify(""), 204
    users_list, next_page = paginate_list(showed_up, per_page)
    json = return_jsonified_users(users_list, showed_up_len, next_page)
    return json, 200


@events.route("/event/<int:event_id>/left", methods=["GET"])
@requires_auth
def return_left(event_id):
    """Endpoint which returns all users who left event

    Properties:
        event_id: id of event

    Returns:
        200: users, next_page and list_len in json
        404: if event not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    event = return_event(event_id)
    left = event.left
    left_len = len(left)
    if left_len == 0:
        return jsonify(""), 204
    users_list, next_page = paginate_list(left, per_page)
    json = return_jsonified_users(users_list, left_len, next_page)
    return json, 200


@events.route("/event/<int:event_id>/posts", methods=["GET"])
@requires_auth
def return_posts(event_id):
    """Endpoint which returns all posts on the event

    Properties:
        event_id: id of event

    Returns:
        200: posts, next_page and list_len in json
        404: if event not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    event = return_event(event_id)
    posts = event.posts
    posts_len = len(posts)
    if posts_len == 0:
        return jsonify(""), 204
    posts_list, next_page = paginate_list(posts, per_page)
    json = return_jsonified_posts(posts_list, posts_len, next_page)
    return json, 200
