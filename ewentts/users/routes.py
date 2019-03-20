"""Module for handling requests on /user endpoints

Attributes:
    users: flask Blueprint for calling user endpoints

"""

from flask import Blueprint, jsonify, request
from firebase_admin import auth
from google.appengine.ext import ndb

from ewentts.models import User, DeletedUser
from ewentts.utils import requires_auth, request_uid, return_jsonified_users, return_jsonified_events, get_per_page, \
    return_user, paginate_list, check_user_authorised
from .utils import create_user, user_exists, jsonify_user, return_edited_user, logger, follow_user

users = Blueprint("users", __name__)


@users.route("/user", methods=["POST"])
@requires_auth
def register():
    """
    Endpoint for creating users.

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
        200: if event already exists, properties of user in json
        201: properties of user in json
        400: if information about user cannot be extracted from firebase or if the information are not valid
        405: if other method then POST used
    """
    user_id = request_uid()
    if user_exists(user_id):
        user = ndb.Key(User, user_id).get()
        code = 200
    else:
        fire_user = auth.get_user(user_id)
        user = create_user(fire_user, user_id)
        code = 201
    json = jsonify_user(user)
    return json, code


@users.route("/user/<string:user_id>", methods=["GET"])
@requires_auth
def view_profile(user_id):
    """Endpoint which returns user properties

    Properties:
        user_id: id of user which is to be viewed

    Returns:
        200: properties of user in json
        404: if user not found
        405: if other method then GET used
    """
    current_user_id = request_uid()
    user = return_user(user_id)
    if current_user_id == user_id:
        logger.info("user: {} gets info about his profile".format(user_id))
        json = jsonify_user(user)
    else:
        logger.info("user: {} gets info about user: {}".format(current_user_id, user_id))
        json = jsonify(username=" ".join(user.user_names),
                       profile_picture_url=user.profile_picture_url,
                       user_email=user.user_email)
    return json, 200


@users.route("/user/<string:user_id>", methods=["DELETE"])
@requires_auth
def delete_user(user_id):
    """Endpoint which deletes user

    Properties:
        user_id: id of user which is to be deleted

    Returns:
        200: message that event was deleted in json
        403: if user without right to delete this user calls this endpoint
        404: if user not found
        405: if other method then DELETE used
    """
    current_user_id = request_uid()
    if check_user_authorised(current_user=current_user_id, authorised_user=user_id):
        user = return_user(user_id)
        deleted_user = DeletedUser(user_names=user.user_names,
                                   profile_picture_url=user.profile_picture_url,
                                   user_id=user.key.id(),
                                   user_email=user.user_email)
        user.key.delete()
        json = jsonify_user(deleted_user)
        return json, 200


@users.route("/user/<string:user_id>/edit", methods=["POST"])
@requires_auth
def edit_user(user_id):
    """Endpoint which edits user

    These properties can get edited if valid values received in json body:
     user_email: email string, optional
     profile_picture_url: picture url string, optional

    Properties:
        user_id: id of user which is to be edited

    Returns:
        200: properties of user in json
        400: if any of the properties in body are not valid
        403: if user without right to edit this user calls this endpoint
        404: if user not found
        405: if other method then POST used
    """
    current_user_id = request_uid()
    user = return_user(user_id)
    if check_user_authorised(current_user=current_user_id, authorised_user=user_id):
        body = request.get_json()
        user = return_edited_user(user, body)
        json = jsonify_user(user)
        return json, 200


@users.route("/user/<string:user_id>/followers", methods=["GET"])
@requires_auth
def return_followers(user_id):
    """Endpoint which returns all followers

    Properties:
        user_id: id of user

    Returns:
        200: users, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    followers = user.followers
    followers_len = len(followers)
    if followers_len == 0:
        return 204
    user_list, next_page = paginate_list(followers, per_page)
    json = return_jsonified_users(user_list, followers_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/following", methods=["GET"])
@requires_auth
def return_following(user_id):
    """Endpoint which returns all following

    Properties:
        user_id: id of user

    Returns:
        200: users, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    following = user.following
    following_len = len(following)
    if following_len == 0:
        return 204
    user_list, next_page = paginate_list(following, per_page)
    json = return_jsonified_users(user_list, following_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/organised_events", methods=["GET"])
@requires_auth
def return_organised_events(user_id):
    """Endpoint which returns all events organised by the user

    Properties:
        user_id: id of user

    Returns:
        200: events, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    organised_events = user.organised_events
    organised_events_len = len(organised_events)
    if organised_events_len == 0:
        return 204
    event_list, next_page = paginate_list(organised_events, per_page)
    json = return_jsonified_events(event_list, organised_events_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/attending_events", methods=["GET"])
@requires_auth
def return_attending_events(user_id):
    """Endpoint which returns all events the user is attending

    Properties:
        user_id: id of user

    Returns:
        200: events, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    attending_events = user.attending_events
    attending_events_len = len(attending_events)
    if attending_events_len == 0:
        return 204
    event_list, next_page = paginate_list(attending_events, per_page)
    json = return_jsonified_events(event_list, attending_events_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/declined_events", methods=["GET"])
@requires_auth
def return_declined_events(user_id):
    """Endpoint which returns all events user has declined

    Properties:
        user_id: id of user

    Returns:
        200: events, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    declining_events = user.declined_events
    declining_events_len = len(declining_events)
    if declining_events_len == 0:
        return 204
    event_list, next_page = paginate_list(declining_events, per_page)
    json = return_jsonified_events(event_list, declining_events_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/visited_events", methods=["GET"])
@requires_auth
def return_visited_events(user_id):
    """Endpoint which returns all events user has visited

    Properties:
        user_id: id of user

    Returns:
        200: events, next_page and list_len in json
        404: if user not found
        405: if other method then GET used
    """
    per_page = get_per_page()
    user = return_user(user_id)
    visited_events = user.visited_events
    visited_events_len = len(visited_events)
    if visited_events_len == 0:
        return 204
    event_list, next_page = paginate_list(visited_events, per_page)
    json = return_jsonified_events(event_list, visited_events_len, next_page)
    return json, 200


@users.route("/user/<string:user_id>/follow", methods=["POST"])
@requires_auth
def follow(user_id):
    """Endpoint which follows the user

    Properties:
        user_id: id of user which current user is to follow

    Returns:
        200: properties of user in json
        404: if user not found
        405: if other method then POST used
    """
    current_user_id = request_uid()

    user = follow_user(current_user_id, user_id)

    json = jsonify_user(user)
    return json, 200
