import inspect
import logging
import re
from functools import wraps

from firebase_admin import auth
from flask import request, abort, jsonify
from geopy import Point, distance
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from ewentts.models import Event, User

logger = logging.getLogger('ewentts.utils')


class BadRequestError(Exception):
    """Raise Error when incorrect data was send to the server"""


class ForbiddenError(Exception):
    """Raise Error when current user does not have right to perform action"""


class NotFoundError(Exception):
    """Raise Error if page|entity not found"""


def error_decorator(f):
    """Decorator to catch errors and abort them to error handlers

    Properties:
        f: function where possible error could appear

    Returns:
        if function runs without error, returns result of the function
        if error occurs aborts with appropriate error key

    """
    print("wrapped func")
    print(f.__name__)

    @wraps(f)
    def function_wrapper(*args, **kwargs):
        try:
            error_message = False
            result = f(*args, **kwargs)
        except BadRequestError as error:
            status = {"type": "Bad Request", "code": 400}
            error_message = str(error)
        except ForbiddenError as error:
            error_message = str(error)
            status = {"type": "Forbidden", "code": 403}
        except NotFoundError as error:
            error_message = str(error)
            status = {"type": "Not Found", "code": 404}
        except Exception as error:
            error_message = str(error)
            status = {"type": "Server Error", "code": 500}
        finally:
            if error_message:
                err = {
                 "error_message": error_message,
                 "source_function": f.__name__,
                 "source_file": inspect.getmodule(f).__name__,
                 "code": status["code"],
                 "title": status["type"]
                 }
                return abort(status["code"], err, f)
            return result
    return function_wrapper


@error_decorator
def request_decoded_token():
    """Tries to verify and get decoded token from firebase"""
    try:
        bearer, token = request.headers.get("Authorization").split(" ")
        logger.info("token received")
        decoded_token = auth.verify_id_token(token)
        logger.info("token decoded")
        return decoded_token
    except AttributeError:
        raise ForbiddenError("No token received")
    except ValueError:
        raise ForbiddenError("Invalid token received")


def requires_auth(f):
    """Decorator checking if user uses correct token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info("requesting decoded token")
        request_decoded_token()
        return f(*args, **kwargs)
    return decorated


def request_uid():
    """Return uid"""
    token = request_decoded_token()
    logger.info("token requested")
    uid = token["uid"]
    logging.info("uid extracted %s", uid)
    return uid


def return_jsonified_users(users, list_len=False, next_page=False):
    """Return users in json

    Properties:
        users: list of users to be transformed to json
        list_len: total length of user list, if False length not defined
        next_page: link to the next page of users, if False this is the last page

    Returns:
        users, next_page, list_len in json
            users contain dictionary with:
                user_names: string, user's name
                user_id: string, unique user id
                profile_picture_url: string, link to user's profile picture
                user_email: string, user's email
    """
    user_list = []
    for user in users:
        user_list += [{"user_names": " ".join(user.user_names),
                       "user_id": user.key.id(),
                       "profile_picture_url": user.profile_picture_url,
                       "user_email": user.user_email}]
    json = {"users": user_list,
            "next_page": next_page,
            "list_len": list_len}
    return jsonify(json)


def return_jsonified_events(events, list_len=False, next_page=False):
    """Return events in json

    Properties:
        events: list of events to be transformed to json
        list_len: total length of event list, if False length not defined
        next_page: link to the next page of events, if False this is the last page

    Returns:
        events, next_page, list_len in json
            events contain dictionary with:
                event_name: string, event name
                user_id: integer, unique event id
                start_datetime: datetime, time and date when event starts
                end_datetime: datetime, time and date when event ends
                location: tuple of floats, location of the event
                event_picture_url: string, link to event's picture
                description: string, description of the event
                private: boolean, if event if private
                organiser: string, event organisers name
    """
    event_list = []
    for event in events:
        organiser = event.organiser.get()
        event_list += [{"event_name": event.event_name,
                        "event_id": event.key.id(),
                        "event_status": event.status,
                        "start_datetime": event.start_datetime.isoformat(),
                        "end_datetime": event.end_datetime.isoformat(),
                        "location": [str(event.latitude), str(event.longitude)],
                        "event_picture_url": event.event_picture_url,
                        "description": event.description,
                        "private": event.private,
                        "organiser": " ".join(organiser.user_names)}]
    json = {"events": event_list,
            "next_page": next_page,
            "list_len": list_len}
    return jsonify(json)


def validate_picture_url(image_url):
    """Validate if picture url is valid

    Properties:
       image_url: string

    Returns:
        True: If image_url is valid
    Raises:
        ValueError: if image_url is not valid
    """
    try:
        if not re.match(r"(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)", image_url):
            raise ValueError("image url: %s is not and image", image_url)
        else:
            return True
    except:
        raise ValueError("image url: %r received in wrong format", image_url)


@error_decorator
def get_body_in_json():
    """Extracts body and returns it in json

    Returns:
        body in json if present,
    Raises:
        BadRequestError: if body is not present
    """

    body = request.get_json()
    if body:
        logger.info("body requested")
        return body
    logger.error("request does not contain body in json")
    raise BadRequestError("request does not contain body in json")


@error_decorator
def return_event(event_id):
    """Returns event based on event id

    Properties:
       event_id: unique event id

    Returns:
        event of class Event if event with the id exists
    Raises:
        NotFoundError: if event not found
    """
    event = ndb.Key(Event, event_id).get()
    if not event:
        logger.error("event: %s does not exist", event_id)
        raise NotFoundError("Event with this ID does not exist")
    return event


def paginate(query, per_page):
    """Checks which page is called and based on it returns results of query

    Properties:
       query: query of events, users or posts
       per_page: number of how many entities are to be returned per page

    Returns:
        results: list of entities
        next_page: link to the next page
    """
    try:
        cursor = ndb.Cursor.from_websafe_string(request.args.get("cursor"))
        logger.info("no cursor received or received in wrong format")
    except:
        logger.info("first page called")
        cursor = ndb.Cursor.from_websafe_string("")
    (results, cursor, more) = query.fetch_page(per_page, start_cursor=cursor)
    if more:
        next_page = cursor.urlsafe()
    else:
        next_page = False

    return results, next_page


def get_per_page():
    """Extract per_page property


    Returns:
        per_page, extracted, if not provided or provided in wrong format returns value 10
    """
    try:
        per_page = request.args.get("per_page")
        if per_page:
            per_page = int(per_page)
    except Exception as e:
        logger.warning(e)
        per_page = 10
    if not per_page:
        logger.info("argument per_page not received, setting to default 10")
        per_page = 10
    return per_page


@error_decorator
def return_user(user_id):
    """Returns user based on user id

    Properties:
       user_id: unique user id

    Returns:
        user of class User if user with the id exists

    Raises:
        NotFoundError: if user with the received id does not exist
    """
    user = ndb.Key(User, user_id).get()
    if not user:
        logger.error("user {} does not exist".format(user_id))
        raise NotFoundError("User with this ID does not exist")
    return user


@error_decorator
def paginate_list(received_list, per_page):
    """Returns event based on event id

    Properties:
        received_list: list of received entities
        per_page: number of how many entities are to be returned per page

    Returns:
        paginated_list: paginated list of entities
        next_page: link to the next page

    Raises:
        BadRequestError: when cursor out of range
    """
    try:

        cursor = int(request.args.get("cursor"))
    except Exception as e:
        logger.warning(e)
        cursor = 0
        logger.warning("cursor not received or received in wrong format")
    try:
        paginated_keys = [received_list[i:i + per_page] for i in range(0, len(received_list), per_page)][cursor]
    except Exception:
        raise BadRequestError("cursor out of range")
    try:
        paginated = [received_list[i:i + per_page] for i in range(0, len(received_list), per_page)][cursor + 1]
        next_page = cursor + 1
    except:
        logger.info("this is the last page")
        next_page = False
    paginated_list = []
    for key in paginated_keys:
        paginated_list += [key.get()]
    return paginated_list, next_page


@error_decorator
def check_user_authorised(current_user, authorised_user):
    """Return True if current_user is equal to authorised_user,
    Othervise raise ForbiddenError"""
    if current_user == authorised_user:
        return True
    raise ForbiddenError("Current user is not authorised to perform this action")


def validate_location(lat, lon):
    """Validate if location is valid

    Properties:
       lat: float, latitude
       lon: lon, latitude

    Returns:
        True: If both lat and lon valid
    Raises:
        ValueError: if lat or lon is not valid
    """
    if lat < -90 or lat > 90:
        logger.error("latitude error")
        raise ValueError("latitude not valid")
    elif lon < -180 or lon > 180:
        logger.error("longitude error")
        raise ValueError("longitude not valid")
    else:
        return True


def generate_location_search_boundaries(original_location, search_range=10):
    """Generate boundaries for location search and return them as a dictionary

    Properties:
       original_location: location of point from where boundaries are measured
       search_range: range of boundaries from the original point

    Returns:
        Dictionary of boundaries: maxlatitude, maxlongitude, minlatitude, minlongitude
    """
    start = Point(original_location)
    d = distance.VincentyDistance(kilometers=search_range)
    boundaries = dict()
    new_point = d.destination(point=start, bearing=0)
    boundaries["maxlatitude"] = new_point.latitude
    new_point = d.destination(point=start, bearing=90)
    boundaries["maxlongitude"] = new_point.longitude
    new_point = d.destination(point=start, bearing=180)
    boundaries["minlatitude"] = new_point.latitude
    new_point = d.destination(point=start, bearing=270)
    boundaries["minlongitude"] = new_point.longitude
    return boundaries


def create_task_change_status_to_present(event):
    """Create task which change status of event to present when due

    Properties:
       event: entity of class Event
    """
    event_id = event.key.id()
    start_datetime = event.start_datetime
    url = "/tasks/change_status_to_present?event_id=" + str(event_id)
    taskqueue.add(method="GET", url=url, queue_name="events-status-to-present", name=str(event_id),
                  eta=start_datetime)


def create_task_change_status_to_past(event_id):
    """Create task which change status of event to past when due

    Properties:
       event: entity of class Event
    """
    event = return_event(event_id)
    end_datetime = event.end_datetime
    url = "/tasks/change_status_to_past?event_id=" + str(event_id)
    taskqueue.add(method="GET", url=url, queue_name="events-status-to-past", name=str(event_id), eta=end_datetime)


def delete_task(queue_name, task_name):
    """Delete task from queue queue_name by task_name"""
    q = taskqueue.Queue(queue_name)
    q.delete_tasks(taskqueue.Task(name=task_name))
