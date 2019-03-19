from flask import Blueprint, jsonify, request, abort

from ewentts.models import Event
from ewentts.utils import requires_auth, return_jsonified_events, return_jsonified_users, get_per_page, paginate
from utils import perform_users_search, logger, perform_events_search_by_name, perform_event_name_query, \
    perform_events_search_by_day, perform_location_query, perform_events_search_by_datetime

search = Blueprint("search", __name__)


@search.route("/search/user", methods=["GET"])
@requires_auth
def search_users():
    """Search users

    Properties:
        body in json containing strings name and optional name2, optional per_page

    Returns:
        200: users, next_page and list_len in json
        204: if no users are found
        400: if name or name2 are not in correct format
        405: if other method then GET used
    """
    name1 = request.args["name"]
    name2 = request.args.get("name2")
    per_page = get_per_page()
    users, next_page = perform_users_search(name1, name2, per_page)
    logger.info("search finished")
    if not users:
        return jsonify(""), 204
    json = return_jsonified_users(users, next_page=next_page)
    return json


@search.route("/search/events/names/", methods=["GET"])
@requires_auth
def search_events_by_names():
    """Search events by names

    Properties:
        body in json containing strings event_name1 and optional event_name2, optional per_page

    Returns:
        200: events, next_page and list_len in json
        204: if no events are found
        400: if event_name1 or event_name2 are not in correct format or no properties received
        405: if other method then GET used
    """
    event_name1 = request.args.get("event_name1")
    event_name2 = request.args.get("event_name2")
    per_page = get_per_page()

    events, next_page = perform_events_search_by_name(event_name1, event_name2, per_page)
    if not events:
        return jsonify(""), 204
    json = return_jsonified_events(events, next_page=next_page)
    return json


@search.route("/search/events/", methods=["GET"])
@requires_auth
def search_events():
    """Search events by names

    Properties:
        body in json possibly containign:
            event_name: string, optional
            latitude: string, optional
            longitude: string, optional
            day: date type, optional
            start_datetime: datetime, optional
            per_page: integer, optional

    Returns:
        200: events, next_page and list_len in json
        204: if no events are found
        400: if properties were not received in the right format
        405: if other method then GET used
    """
    per_page = get_per_page()
    query = Event.query()

    event_name = request.args.get("event_name")
    if event_name:
        logger.debug("event_name received as search parameter")
        query = perform_event_name_query(query, event_name)
        logger.info("search by event name finished")

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    if latitude and longitude:
        location = (float(latitude), float(longitude))
        print(location)
        print(type(location))
        logger.info("location received as search parameter")
        query = perform_location_query(query, location)
        logger.info("search by location finished")
    day = request.args.get("day")
    if day:
        logger.info("start datetime received as search parameter")
        query = perform_events_search_by_day(query, day)
        logger.info("search by start_datetime finished")

    start_datetime = request.args.get("start_datetime")
    if start_datetime:
        logger.info("start datetime received as search parameter")
        query = perform_events_search_by_datetime(query, start_datetime)
        logger.info("search by start_datetime finished")
    events, next_page = paginate(query, per_page)
    logger.info("search finished")
    if not events:
        return jsonify(""), 204
    json = return_jsonified_events(events, next_page=next_page)
    return json
