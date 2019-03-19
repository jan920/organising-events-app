import logging
from flask import request
from datetime import datetime, date, time, timedelta

from ewentts.models import User, Event
from ewentts.utils import paginate, generate_location_search_boundaries, error_decorator, BadRequestError, \
    validate_location

logger = logging.getLogger("search")


def return_next_letter(letter):
    """Return next letter in the alphabet"""
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    return alphabet[alphabet.index(letter) + 1]


def return_next_name(name):
    """Return name which would be in dictionary directly after name received

    Properties:
        name: string

    Returns:
        name which would be in dictionary directly after name received
    Raises:
        BadRequestError if name is not non empty string
    """
    try:
        name = name.lower()
    except:
        raise BadRequestError("Value other then non empty string entered as parameter")
    next_name = ""
    for letter in name[::-1]:
        if letter == "z":
            next_name = "a" + next_name
        else:
            next_letter = return_next_letter(letter)
            x = len(name)-1-len(next_name)
            next_name = name[:x] + next_letter + next_name
            return next_name.capitalize()
    return None


@error_decorator
def perform_name_query(query, name):
    """Perform name query

    Properties:
        query: query which is to be filtered by name search
        name: string, used for filtering query

    Returns:
        query
    """
    next_name = return_next_name(name)
    if next_name:
        query = query.filter(User.user_names >= name.capitalize(), User.user_names < next_name.capitalize())
    else:
        query = query.filter(User.user_names >= name.capitalize())
    return query


def perform_users_search(name1, name2, per_page):
    """Perform search for users

    Properties:
        name1: string
        name2: string/Null
        per_page: integer how many users to be returned per page

    Returns:
        users: list of filtered users of length per_page
        next_page: link to the next page
    """
    query1 = User.query()
    query1 = perform_name_query(query1, name1)
    if name2:
        query2 = User.query()
        query2 = perform_name_query(query2, name2)
        users = list(set(query1.fetch()).intersection(set(query2.fetch())))
        next_page = False
    else:
        users, next_page = paginate(query1, per_page)
    return users, next_page


def perform_event_name_query(query, name):
    """Filter events by name query

    Properties:
        query: query of events which is to be filtered by name search
        name: string

    Returns:
        query: query of events filtered by name
    """
    next_name = return_next_name(name)
    if next_name:
        query = query.filter(Event.event_name >= name.capitalize(), Event.event_name < next_name.capitalize())
    else:
        query = query.filter(Event.event_name >= name.capitalize())
    return query


@error_decorator
def perform_events_search_by_name(event_name1, event_name2, per_page):
    """Search events by name

    Properties:
        event_name1: string
        event_name2: string/Null
        per_page: integer how many users to be returned per page

    Returns:
        events: list of filtered events of length per_page
        next_page: link to the next page

    Raises:
        BadRequestError: if event_name1 not received
    """
    if not event_name1:
        logger.error("no names received")
        raise BadRequestError("event_name1 not received")
    query1 = Event.query()
    query1 = perform_event_name_query(query1, event_name1)
    if event_name2:
        query2 = Event.query()
        query2 = perform_event_name_query(query2, event_name2)
        events = list(set(query1.fetch()).intersection(set(query2.fetch())))
        next_page = False
    else:
        events, next_page = paginate(query1, per_page)
    logger.info("search by event names finished")
    return events, next_page


def search_today(query):
    """Filter query so it contains only events happening today

    Properties:
        query: query of events which is to be filtered

    Returns:
        query: query of events happening today
    """
    today = date.today()
    today_min = datetime.combine(today, time.min)
    today_max = datetime.combine(today, time.max)
    query = query.filter(Event.start_datetime > today_min, Event.start_datetime < today_max)
    return query


def search_tomorrow(query):
    """Filter query so it contains only events happening tomorrow

    Properties:
        query: query of events which is to be filtered

    Returns:
        query: query of events happening tomorrow
    """
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_min = datetime.combine(tomorrow, time.min)
    tomorrow_max = datetime.combine(tomorrow, time.max)
    query = query.filter(Event.start_datetime > tomorrow_min, Event.start_datetime < tomorrow_max)
    return query


def search_other_day(query, day):
    """Filter query so it contains only events happening the day received

    Properties:
        query: query of events which is to be filtered
        day: date object by which the query is to be filtered

    Returns:
        query: query of events happening on certain day
    """
    return query


def perform_events_search_by_day(query, start_datetime):
    """Filter query so it contains only events on certain date

    Properties:
        query: query of events which is to be filtered
        start_datetime: datetime object|string containing "today" or "tomorrow"

    Returns:
        query: query of events happening on certain day
    """
    if start_datetime == "today":
        query = search_today(query)
    elif start_datetime == "tomorrow":
        query = search_tomorrow(query)
    else:
        day = start_datetime.date()
        query = search_other_day(query, day)
    return query


@error_decorator
def perform_location_query(query, point):
    """Filter query so it contains only events in certain location

    Properties:
        query: query of events which is to be filtered
        point: point from which distance of query is to be measured
        location_range: float, optional, range of location query

    Returns:
        query: query of events happening in certain location in distance from point received

    Raises:
        BadRequestError if location or location received out of range or in wrong format
    """
    try:
        validate_location(point)
    except ValueError as e:
        logger.error("location received in wrong format")
        raise BadRequestError(e)

    location_range = request.args.get("location_range")
    if location_range:
        try:
            location_range = int(location_range)
            if location_range > 100 or location_range < 0:
                raise BadRequestError("location_range is not between 0 and 100 km")
        except BadRequestError as e:
            logger.error("location_range received in wrong format")
            logger.error(e)
            raise BadRequestError(e)
        except (TypeError, ValueError):
            logger.error("location_range received in wrong format")
            raise BadRequestError("location_range received in wrong format")
    else:
        location_range = 10

    boundaries = generate_location_search_boundaries(point, location_range)
    print(123)
    print(boundaries)
    longitudes_distance = boundaries["maxlongitude"] - boundaries["minlongitude"]
    if 0 < longitudes_distance < 180:
        print(boundaries["maxlongitude"])
        print(boundaries["minlongitude"])
        query = query.filter(Event.longitude > boundaries["minlongitude"], Event.longitude < boundaries["maxlongitude"])
    elif longitudes_distance < -180:
        print(boundaries["maxlongitude"])
        print(boundaries["minlongitude"])
        query = query.filter(Event.longitude > boundaries["minlongitude"], Event.longitude < boundaries["maxlongitude"])
    else:
        print(boundaries["minlongitude"])
        print(boundaries["maxlongitude"])
        query = query.filter(Event.longitude > boundaries["maxlongitude"], Event.longitude < boundaries["minlongitude"])
    query = query.filter(Event.latitude < boundaries["maxlatitude"], Event.latitude > boundaries["minlatitude"])
    return query


def perform_events_search_by_datetime(query, start_datetime):
    """Will perform search by datatime query but currently not implemented"""
    return query
