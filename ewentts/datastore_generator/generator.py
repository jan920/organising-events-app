from datetime import datetime, timedelta

import pytz
import logging
from dateutil.parser import parse
from firebase_admin import auth
from flask import Blueprint, jsonify, request
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from ewentts.utils import return_event, create_task_change_status_to_present, create_task_change_status_to_past
from ewentts.events.utils import create_event
from ewentts.models import User, Event
from ewentts.users.utils import create_user


generator = Blueprint("generator", __name__)

logger = logging.getLogger("generator")


@generator.route('/generate', methods=["GET"])
def generate():
    """Generates events and users"""
    timezone = pytz.timezone("UTC")
    user_id = "olG4S8Ss7xVjMpmwb6Q5vN4tG2J3"
    user = User(id=user_id,
                user_names=["Miroslav", "Matocha"],
                profile_picture_url="https://i.imgur.com/nqTGipe.jpg",
                user_email="mira.matocha1234@seznam.cz")
    user_key = user.put()
    start_datetime = datetime.now() + timedelta(days=5)
    start_datetime = timezone.localize(start_datetime)
    bodies = [{"event_name": "Event Name",
               "start_datetime": str(start_datetime),
               "location": [15.395470, 15.590950],
               "event_picture_url": "https://i.imgur.com/nqTGipe.jpg",
               "description": "description",
               "private": True}]
    start_datetime = datetime.now() + timedelta(weeks=40)
    start_datetime = timezone.localize(start_datetime)
    end_datetime = start_datetime + timedelta(days=4)
    bodies += [{"event_name": "Events Name",
                "start_datetime": str(start_datetime),
                "end_datetime": str(end_datetime),
                "location": [20.396476, 10.588913],
                "event_picture_url": "https://i.imgur.com/nqTGipe.jpg",
                "description": "description",
                "private": False}]
    start_datetime = datetime.now() + timedelta(weeks=35)
    start_datetime = timezone.localize(start_datetime)
    end_datetime = start_datetime + timedelta(days=4)
    bodies += [{"event_name": "Party na byte",
                "start_datetime": str(start_datetime),
                "end_datetime": str(end_datetime),
                "location": [15.401938, 20.600071],
                "event_picture_url": "https://i.imgur.com/nqTGipe.jpg",
                "description": "description",
                "private": True}]
    start_datetime = datetime.utcnow()
    timezone = pytz.timezone("UTC")
    start_datetime = timezone.localize(start_datetime)
    start_datetime += timedelta(hours=1)
    end_datetime = start_datetime + timedelta(hours=10)
    bodies += [{"event_name": "Today party",
                "start_datetime": str(start_datetime),
                "end_datetime": str(end_datetime),
                "location": [49.401938, 15.600071],
                "event_picture_url": "https://i.imgur.com/nqTGipe.jpg",
                "description": "description",
                "private": True}]
    start_datetime = datetime.utcnow()
    timezone = pytz.timezone("UTC")
    start_datetime = timezone.localize(start_datetime)
    start_datetime += timedelta(days=1)
    end_datetime = start_datetime + timedelta(days=1)
    bodies += [{"event_name": "Tomorrow party",
                "start_datetime": str(start_datetime),
                "end_datetime": str(end_datetime),
                "location": [49.401938, 15.600071],
                "event_picture_url": "https://i.imgur.com/nqTGipe.jpg",
                "description": "description",
                "private": True}]

    for body in bodies:
        event = create_event(body, user_id)

    event_id = 1234

    event = Event(id=event_id,
                  event_name="Test Event Name",
                  status="future",
                  start_datetime=(datetime.now() + timedelta(weeks=100, days=2)),
                  end_datetime=(datetime.now() + timedelta(weeks=100)),
                  latitude=49.401938,
                  longitude=15.600071,
                  location=ndb.GeoPt(49.401938, 15.600071),
                  event_picture_url="https://i.imgur.com/nqTGipe.jpg",
                  description="test description",
                  private=True,
                  organiser=user_key,
                  guest_list=[user_key],
                  attendees=[user_key],
                  showed_up=[user_key],
                  left=[user_key])

    event_key = event.put()

    user_id = "1234"
    user = User(id=user_id,
                user_names=["Test", "User"],
                profile_picture_url="https://i.test.com/test.jpg",
                user_email="test.user@gmail.com",
                followers=[user_key],
                following=[user_key],
                organised_events=[event_key],
                attending_events=[event_key],
                declined_events=[event_key],
                visited_events=[event_key],)

    user.put()

    user_id = "UVTBYMr264M8h2fKUGvb1pIN41f2"

    fire_user = auth.get_user(user_id)
    user = create_user(fire_user, user_id)

    user_key = user.put()

    event_id = 2345

    event = Event(id=event_id,
                  event_name="Test Event Name",
                  status="future",
                  start_datetime=(parse("2019-12-03T10:15:30")),
                  end_datetime=(parse("2020-12-03T10:15:30")),
                  latitude=49.401938,
                  longitude=15.600071,
                  event_picture_url="https://i.imgur.com/nqTGipe.jpg",
                  description="test description",
                  private=True,
                  organiser=user_key,
                  guest_list=[user_key],
                  attendees=[user_key],
                  showed_up=[user_key],
                  left=[user_key])

    event.put()

    return jsonify(guest_list=["1234", "123"]), 201


@generator.route('/tasks/create_change_status_for_next_week', methods=["GET"])
def create_change_status_for_next_week():
    """Create task for each event happening next week to change it's status"""
    query = Event.query()
    events = query.filter(Event.start_datetime > datetime.now(), Event.start_datetime < datetime.now()
                          + timedelta(days=7))
    for event in events:
        create_task_change_status_to_present(event)
    return "done"


@generator.route('/tasks/change_status_to_present', methods=["GET"])
def change_status_to_present():
    """Change event status to present"""
    event_id = request.args.get("event_id")
    event_id = int(event_id)
    event = return_event(event_id)
    event.status = "present"
    event.put()
    create_task_change_status_to_past(event_id)
    return "done"


@generator.route('/tasks/change_status_to_past', methods=["GET"])
def change_status_to_past():
    """Change event status to past"""
    event_id = request.args.get("event_id")
    event_id = int(event_id)
    event = return_event(event_id)
    event.status = "past"
    event.put()
    return "done"


@generator.route('/tasks/search_api_test', methods=["GET"])
def search_api_test():
    event_id = 1234
    event = return_event(event_id)
    from google.appengine.api import search
    index = search.Index(name="testsearch")
    fields = [
        search.TextField(name="event_name", value=event.event_name),
        search.DateField(name="start_datetime", value=event.start_datetime),
        search.DateField(name="end_datetime", value=event.end_datetime),
        search.AtomField(name="event_private", value=str(event.private)),
        search.AtomField(name="event_state", value=event.status),
        search.GeoField(name="location", value=search.GeoPoint(latitude=event.latitude, longitude=event.longitude))]
#        value=search.geopoint(event.location))]
#        add fields- location
    doc = search.Document(doc_id=str(event_id), fields=fields)
    try:
        add_result = search.Index(name="testsearch").put(doc)
        add_result[0].id
    except search.Error:
        print(search.Error)
    for index in search.get_indexes(fetch_schema=True):
        logging.info("index {}".format(index.name))
        logging.info("schema: {}".format(index.schema))

    query = "True"
    index = search.Index("testsearch")
    search_results = index.search(query)
    for doc in search_results:
        print("printing doc...... \n.....\n....")
        print(doc)

    querystring = "True"
    querystring = "event_name:\"Test\" AND event_state:\"future\""
    index = search.Index("testsearch")
    search_query = search.Query(
        query_string=querystring,
        options=search.QueryOptions(
            limit=10))
    search_results = index.search(search_query)
    number_found = search_results.number_found
    print(number_found)
    for doc in search_results:
        print(doc.doc_id)
        print(doc.fields)

    return "all done"
