import inspect
import logging
import re

from flask import jsonify
from google.appengine.ext import ndb

from ewentts.models import User
from ewentts.utils import validate_picture_url, error_decorator, BadRequestError, return_user

logger = logging.getLogger('users')


def user_exists(user_id):
    """Check if user already exists based on user_id"""
    if ndb.Key(User, user_id).get():
        logger.warning("user: %s exists", user_id)
        return True
    logger.debug("user does not exist yet")
    return False


@error_decorator
def create_user(fire_user, user_id):
    """Create user of class User

    Properties:
        fire_user: properties about user gained through firebase
        user_id: unique user_id

    Returns:
        user of Class User

    Raises:
        BadRequestError: if information extracted from firebase about user is not valid
    """
    try:
        names = fire_user.display_name.split(" ")
        profile_picture_url = fire_user.photo_url
        validate_picture_url(profile_picture_url)
        email = fire_user.email
        validate_email(email)
        logger.debug("information about user extracted from firebase")
    except ValueError as e:
        logger.error("information extracted from firebase is not correct")
        logger.error(e)
        raise BadRequestError(e)
    except Exception:
        logger.error("cannot extract information about user: %s from firebase", user_id)
        raise BadRequestError("The information needed to create user cannot be extracted from firebase")

    user = User(id=user_id,
                user_names=names,
                profile_picture_url=profile_picture_url,
                user_email=email)
    user.put()
    logger.info("user: %s created", user_id)
    return user


def jsonify_user(user):
    """Return properties of user in json

    Properties:
        post: user which is to be viewed

    Returns:
        Properties of user in json:
            user_names: string containing user's name
            profule_picture_url: string with user's profile picture url
            user_id: unique user id
            user_email: string with user's email
    """
    json = jsonify(user_names=" ".join(user.user_names),
                   profile_picture_url=user.profile_picture_url,
                   user_id=user.key.id(),
                   user_email=user.user_email)
    return json


@error_decorator
def edit_user_email(user, user_email):
    """Edit user's emial

    Properties:
        user: user whose email is to be edited
        user_email: new user's email

    Returns:
        If user_email valid return properties of user in json:
            user_names: string containing user's name
            profile_picture_url: string with user's profile picture url
            user_id: unique user id
            user_email: string with user's email

    Raises:
        BadRequestError: if user_email is not in correct format
    """
    try:
        validate_email(user_email)
    except ValueError as e:
        logger.error("email: %s received is not referring to and email", user_email)
        logger.error(e)
        raise BadRequestError(e)
    user.user_email = user_email
    logger.info("user email changed to %s", user_email)
    return user


@error_decorator
def edit_profile_picture_url(user, profile_picture_url):
    """Edit user's profile picture

    Properties:
        user: user whose email is to be edited
        profile_picture_url: string, user's link to new profile picture

    Returns:
        If profile_picture_url valid return properties of user in json:
            user_names: string containing user's name
            profile_picture_url: string with user's profile picture url
            user_id: unique user id
            user_email: string with user's email

    Raises:
        BadRequestError: if profile_picture_url is not valid picture url
    """
    try:
        validate_picture_url(profile_picture_url)
    except ValueError as e:
        logger.error("url: %s is not referring to an image", profile_picture_url)
        logger.error(e)
        raise BadRequestError(e)
    user.profile_picture_url = profile_picture_url
    logger.info("user profile picture changed to %s", profile_picture_url)
    return user


def return_edited_user(user, body):
    """Edit user's profile

    Properties:
        user: user whose profile is to be edited
        body: json object, could optionally could contain user_email or profile_picture_url

    Returns:
        Properties of user in json:
            user_names: string containing user's name
            profile_picture_url: string with user's profile picture url
            user_id: unique user id
            user_email: string with user's email
    """
    logger.info("changes to user received in json")
    user_email = body.get("user_email")
    if user_email:
        user = edit_user_email(user, user_email)
    profile_picture_url = body.get("profile_picture_url")
    if profile_picture_url:
        user = edit_profile_picture_url(user, profile_picture_url)
    user.put()
    logger.info("changes to user profile finished")
    return user


def validate_email(email):
    """Validate email address

    Properties:
       email

    Returns:
        True: If email valid
    Raises:
        ValueError: if email not valid
    """
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("string received: %s is not valid email", email)
        else:
            return True
    except:
        raise ValueError("email: %r received in wrong format", email)


@error_decorator
def follow_user(current_user_id, user_id):
    """Follows user

    Properties:
       current_user_id: user id of user who wants to start following
       user_id: id of user who is to be followed

    Returns:
        user: user entity of class User
    Raises:
        BadRequestError if current_user_id is equal to user_id
    """
    if current_user_id == user_id:
        logger.error("user cannot follow himself")
        raise BadRequestError("User cannot follow himself")
    current_user = ndb.Key(User, current_user_id).get()
    user = return_user(user_id)
    user_key = user.put()
    if user_key not in current_user.following:
        current_user.following += [user_key]
        user.followers += [current_user.put()]
        user.put()
    else:
        logger.warning("user: {}  already follows user: {}".format(current_user_id, user_id))
    return user
