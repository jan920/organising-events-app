"""Module containing functions used by events/routes.py module

Attributes:
    logger: Logger for logging in events package

"""


import logging
from datetime import datetime, timedelta

import pytz
from dateutil.parser import parse
from flask import jsonify
from google.appengine.ext import ndb

from ewentts.models import Event, User
from ewentts.utils import validate_picture_url, request_uid, return_user, validate_location, \
    create_task_change_status_to_present, create_task_change_status_to_past, delete_task, \
    error_decorator, BadRequestError

logger = logging.getLogger("events")


@error_decorator
def create_event(body, user_id):
    """Create event

    :param body: body which should contain all data necessary for creating event
    :param user_id: unique id of user of class User
    :return: properties of the event in json,
            Specifically:   event_name: name of the event
                            event_id: unique id of the event
                            event_status: status if event is future | present | past
                            start_datetime: date and time of start of the event
                            end_datetime: date and time of end of the event
                            location: location of the event as array of floats
                            event_picture_url: url link to the event picture
                            description: description of the event
                            private: boolean if the event is private or nor
                            organiser: name of organiser of the event
    :raise: BadRequestError: if body contains incorrect data or is missing some data
    """
    try:
        event_name = body["event_name"]
        start_datetime = body["start_datetime"]
        end_datetime = body.get("end_datetime")
        location = body["location"]
        event_picture_url = body.get("event_picture_url")
        if not event_picture_url:
            event_picture_url = "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/" \
                                "discount-codes-reach-more-people-eventbrite.png"
        description = body.get("description")
        if not description:
            description = ""
        private = body["private"]
        guest_list = body.get("guest_list")
    except Exception as e:
        logger.error("info required to set up event not received")
        logger.error(e)
        raise BadRequestError("Some of the info required to set up event not received, required info: event_name, "
                              "start_datetime, location, private")
    logger.debug("info required to set up event received")
    organiser_key = ndb.Key(User, user_id)
    utc = pytz.utc
    try:
        validate_picture_url(event_picture_url)
        start_datetime = parse(start_datetime).astimezone(utc)
        start_datetime = start_datetime.replace(tzinfo=None)
        if end_datetime:
            end_datetime = parse(end_datetime).astimezone(utc)
            end_datetime = end_datetime.replace(tzinfo=None)
        else:
            end_datetime = start_datetime + timedelta(days=1)
        validate_start_datetime(start_datetime, end_datetime)
        validate_end_datetime(end_datetime, start_datetime)
        validate_location(*location)
        event = Event(event_name=event_name,
                      status="future",
                      start_datetime=start_datetime,
                      end_datetime=end_datetime,
                      latitude=location[0],
                      longitude=location[1],
                      event_picture_url=event_picture_url,
                      description=description,
                      private=private,
                      organiser=organiser_key,
                      )
        if guest_list:
            invite_users(event, body)
    except ValueError as e:
        logger.error("properties to set up event received in wrong format")
        logger.error(e)
        raise BadRequestError(e)

    event.put()
    if event.start_datetime < datetime.now() + timedelta(days=7):
        create_task_change_status_to_present(event)
    user = return_user(user_id)
    user.organised_events += [event.key]
    user.put()
    logger.info("event {} created".format(event.key.id()))
    return event


def jsonify_event(event):
    """Return properties of event in json

    :param event: object of class Event
    :return: properties of the event in json,
            Specifically:   event_name: name of the event
                            event_id: unique id of the event
                            event_status: status if event is future | present | past
                            start_datetime: date and time of start of the event
                            end_datetime: date and time of end of the event
                            location: location of the event as array of floats
                            event_picture_url: url link to the event picture
                            description: description of the event
                            private: boolean if the event is private or nor
                            organiser: name of organiser of the event
    """
    organiser = event.organiser.get()
    json = jsonify(event_name=event.event_name,
                   event_id=event.key.id(),
                   event_status=event.status,
                   start_datetime=event.start_datetime.isoformat(),
                   end_datetime=event.end_datetime.isoformat(),
                   location=[event.latitude, event.longitude],
                   event_picture_url=event.event_picture_url,
                   description=event.description,
                   private=event.private,
                   organiser=" ".join(organiser.user_names)
                   )
    return json


def return_jsonified_posts(posts, list_len=False, next_page=False):
    """Return list of posts in json

    :param posts: object of class Post
    :param list_len: total length of the list of posts
    :param next_page: link to the next page with continuation of the list of posts
    :return: properties of the posts in json, link to next page and total length
        Specifically:
            next_page: url link to next page where is the next part of the post list
                        if value is false it is the last page and no other page is available
            list_len: total number of all the posts which can be returned
                        if value is false the total number is not available, possibly because the list
                        if very long
            posts: list of posts where each of the item contains dictionary with:
                        creator: the creator of the post
                        post_id: unique id of the post
                        post_datetime: time when the post was created
                        content: the content of the post

    """
    posts_list = []
    for post in posts:
        creator = post.creator.get()
        posts_list += [{"creator": " ".join(creator.user_names),
                        "post_id": post.key.id(),
                        "post_datetime": post.post_datetime.isoformat(),
                        "content": post.content}]
    json = {"posts": posts_list,
            "next_page": next_page,
            "list_len": list_len}

    return jsonify(json)


def edit_event_name(event, event_name):
    """Edits name of the event

    :param event: entity of Class Event
    :param event_name: new event name
    :return: event with edited_name

    """
    event.event_name = event_name
    event.put()
    logger.info("event name edited to {}".format(event_name))
    return event


@error_decorator
def edit_start_datetime(event, start_datetime, end_datetime):
    """Edits start_datetime of the event if valid

    :param event: event for which start datetime should be edited
    :param start_datetime: iso datetime including timezone
    :param end_datetime: iso datetime without timezone
    :return: event
    :raise: BadRequestError if start_datetime is not valid
    """
    utc = pytz.utc
    try:
        start_datetime = parse(start_datetime).astimezone(utc)
        start_datetime = start_datetime.replace(tzinfo=None)
        validate_start_datetime(start_datetime, end_datetime)
    except ValueError as e:
        logger.error(e)
        logger.error("start datetime: {} received in wrong format".format(start_datetime))
        raise BadRequestError(e)
    event.start_datetime = start_datetime
    event.put()
    logger.info("start datetime edited to {}".format(start_datetime))
    return event


@error_decorator
def edit_end_datetime(event, end_datetime, start_datetime):
    """Edits end_datetime of the event if valid

    :param event: event for which start datetime should be edited
    :param end_datetime: iso datetime including timezone
    :param start_datetime: iso datetime without timezone
    :return: event
    :raise: BadRequestError: if end_datetime is not valid
    """
    utc = pytz.utc
    try:
        end_datetime = parse(end_datetime).astimezone(utc)
        end_datetime = end_datetime.replace(tzinfo=None)
        validate_end_datetime(end_datetime, start_datetime)
    except ValueError as e:
        logger.error(e)
        logger.error("end datetime: {} received in wrong format".format(end_datetime))
        raise BadRequestError(e)
    event.end_datetime = end_datetime
    event.put()
    logger.info("end datetime edited to {}".format(end_datetime))
    return event


def edit_datetimes(event, body):
    """Edits start_datetime and end_datime of the event

    Check if body contains start_datetime or end datetime,
    if it does start_datetime or end_datetime of event
    are eddited if valid

    :param event: object of class Event
    :param body: json object containing which might contain start_datetime or end_datetime
    :return: edited event if start_datetime or end_datetime were in
             body, otherwise return event which was received
    """
    start_datetime = body.get("start_datetime")
    end_datetime = body.get("end_datetime")
    if start_datetime and end_datetime:
        utc = pytz.utc
        edit_start_datetime(event, start_datetime,
                            parse(end_datetime).astimezone(utc).replace(tzinfo=None))
        edit_end_datetime(event, end_datetime,
                          parse(start_datetime).astimezone(utc).replace(tzinfo=None))
        create_change_task_to_present_if_event_soon(event)
    elif start_datetime:
        edit_start_datetime(event, start_datetime, event.end_datetime)
        create_change_task_to_present_if_event_soon(event)
    elif end_datetime:
        event = edit_end_datetime(event, end_datetime, event.start_datetime)
    return event


@error_decorator
def edit_location(event, location):
    """Edits location of the event

    Check if location is valid and if it us update location property of the received event

    :param event: object of class Event
    :param location: tuple of floats representing geographic location
    :return: edited event if location is valid, otherwise abort(400) with string describing the error
    """
    try:
        validate_location(*location)

    except ValueError as e:
        logger.error(e)
        logger.error("location: {} {} is not valid location".format(float(location[0]), float(location[1])))
        raise BadRequestError(e)

    event.latitude = location[0]
    event.longitude = location[1]
    event.put()
    logger.info("location edited to {} {}".format(float(location[0]), float(location[1])))
    return event


@error_decorator
def edit_event_picture_url(event, event_picture_url):
    """Edits picture_url of the event

    Check if picture url is valid and if it us update picture_url property of the received event

    :param event: object of class Event
    :param event_picture_url: string containing url link to a picture
    :return: edited event if event_picture_url is valid,
             otherwise abort(400) with string describing the error
    """
    try:
        validate_picture_url(event_picture_url)
    except ValueError as e:
        logger.error(e)
        logger.error("url: {} is not referring to an image".format(event_picture_url))
        raise BadRequestError(e)
    event.event_picture_url = event_picture_url
    event.put()
    logger.info("event picture edited to {}".format(event_picture_url))
    return event


def edit_present_event(event, body):
    """Edits properties allowed to be changed for present event

    Check if body contains end datetime which is only property of event which can be edited when
     event's state is present, if it does end_datetime of event is edited if valid

    :param event: object of class Event
    :param body: json object containing which might contain end_datetime
    :return: edited event if end_datetime was in body, otherwise return event which was received
    """
    end_datetime = body.get("end_datetime")
    if end_datetime:
        event = edit_end_datetime(event, end_datetime, event.start_datetime)
        event_id = event.key.id()
        queue_name = "events-status-to-past"
        task_name = str(event_id)
        delete_task(queue_name, task_name)
        create_task_change_status_to_past(event_id)
    else:
        logger.warning("nothing has been eddited")
    return event


def edit_future_event(event, body):
    """Edits properties allowed to be changed for future event

    Check if body contains start_datetime, end_datetime,
    event_name, event_picture_url or description which are
    only properties of event which can be edited when
    event's state is future, if it does the properties are
    edited if valid

    :param event: object of class Event
    :param body: json object containing which might contain start_datetime, end_datetime, event_name,
    event_picture_url or description
    :return: edited event if any of following were in body start_datetime, end_datetime, event_name,
    event_picture_url or description, otherwise return event which was received
    """
    event_name = body.get("event_name")
    if event_name:
        event = edit_event_name(event, event_name)
    event = edit_datetimes(event, body)
    location = body.get("location")
    if location:
        event = edit_location(event, location)
    event_picture_url = body.get("event_picture_url")
    if event_picture_url:
        event = edit_event_picture_url(event, event_picture_url)
    description = body.get("description")
    if description:
        event.description = description
        logger.info("description edited to {}".format(description))
    event.put()
    logger.debug("event changes saved")
    return event


@error_decorator
def return_edited_event(event, body):
    """Check status of the event received and based on that edit event

    :param event: object of class Event
    :param body: json object containing which might contain parameters for editing event
    :return: event if any of following were in body start_datetime, end_datetime, event_name
             event_picture_url or description, otherwise return event which was received
    :raise: BadRequestError: if event status is past
    """
    if event.status == "past":
        logger.error("The event already finished it can not be edited",)
        raise BadRequestError("The event already finished it can not be edited")
    if event.status == "present":
        event = edit_present_event(event, body)
    else:
        event = edit_future_event(event, body)
    return event


def validate_start_datetime(start_datetime, end_datetime):
    """Validates start_datetime

    Return True if start_datetime is before end_datetime,
    start datetime is in the future and difference between
    start_datetime and end_datetime is no more then 7 days,
    otherwise return ValueError


    :param start_datetime: datetime object
    :param end_datetime: datetime object
    :return: ValueError if start_datetime is not valid, otherwise True
    """
    if start_datetime > datetime.utcnow():
        if end_datetime > start_datetime:
            if end_datetime < start_datetime + timedelta(days=7):
                return True
            raise ValueError("start_datetime: {} is too distant from end_datetime {}, they can be maximum week "
                             "apart".format(start_datetime, end_datetime))
        raise ValueError("end_datetime: {} must be after start datetime: {}".format(end_datetime, start_datetime))
    raise ValueError("start_datetime: {} must be in future".format(start_datetime))


def validate_end_datetime(end_datetime, start_datetime):
    """Validates end_datetime

    Return True if end_datetime is after start_datetime, end_datetime is in the future and difference
    between end_datetime and start_datetime is no more then 7 days, otherwise return ValueError


    :param end_datetime: datetime object
    :param start_datetime: datetime object
    :return: ValueError if end_datetime is not valid, otherwise True
    """
    if end_datetime > datetime.utcnow():
        if end_datetime > start_datetime:
            if end_datetime < start_datetime + timedelta(days=7):
                return True
            raise ValueError("end_datetime: {} is too long in the future, end_datetime can be maximum week "
                             "after start_datetime".format(end_datetime))
        raise ValueError("end_datetime: {} must be after start datetime: {}".format(end_datetime, start_datetime))
    raise ValueError("end_datetime: {} must be in future".format(end_datetime))


@error_decorator
def invite_users(event, body):
    """Adds users to guest list

    If body contains guest_list users according to the user_id
    from guest_list are added to events property guest_list


    :param event: object of class Event
    :param body: json object containing which should
    contain guest_list, list of user_id of users who
    are to be invited to the event
    :return: edited event, i
    :raise: BadRequestError: if guest_list not provided in body
    """
    guest_list = body.get("guest_list")
    if not guest_list:
        logger.error("guest_list not provided in json")
        raise BadRequestError("guest_list not provided in json")
    for user_id in guest_list:
        user_key = ndb.Key(User, user_id)
        if user_key not in event.guest_list:
            event.guest_list += [ndb.Key(User, user_id)]
    event.put()
    return event


def user_attends_event(event):
    """Adds users to attendees

    Current user is addend to list attendees which is property of the event received storing
    all users who are planing to coming on coming, event is added to current users attending_events

    :param event: object of class Event
    :return: edited event
    """
    current_user_id = request_uid()
    current_user = ndb.Key(User, current_user_id).get()
    user_key = current_user.put()
    if user_key not in event.attendees:
        current_user.attending_events += [event.put()]
        event.attendees += [current_user.put()]
        event.put()
    else:
        logger.warning("user: {} already attends event: {}".format(current_user_id, event.key.id()))
    return event


def user_came_to_event(event):
    """Adds users to showed_up

    Current user is addend to list showed_up which is property of the event received storing
    all users who came to the event, event is added to current users visited_events

    :param event: object of class Event
    :return: edited event
    """
    current_user_id = request_uid()
    current_user = ndb.Key(User, current_user_id).get()
    user_key = current_user.put()
    if user_key not in event.showed_up:
        current_user.visited_events += [event.put()]
        event.showed_up += [current_user.put()]
        event.put()
    else:
        logger.warning("user: {} already came to event: {}".format(current_user_id, event.key.id()))
    return event


def user_left_event(event):
    """Adds users to left list

    Current user is addend to list of users who left the event

    :param event: object of class Event
    :return: edited event
    """
    current_user_id = request_uid()
    current_user = ndb.Key(User, current_user_id).get()
    user_key = current_user.put()
    if user_key not in event.left:
        event.left += [current_user.put()]
        event.put()
    else:
        logger.warning("user: {} already left event: {}".format(current_user_id, event.key.id()))
    return event


def create_change_task_to_present_if_event_soon(event):
    """If event starts in next 7 days task which will change
    its status to present when it starts is created"""
    if event.start_datetime < datetime.now() + timedelta(days=7):
        queue_name = "events-status-to-present"
        task_name = str(event.key.id())
        delete_task(queue_name, task_name)
        create_task_change_status_to_present(event)
