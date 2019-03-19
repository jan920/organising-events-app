from google.appengine.ext import ndb

import logging

from flask import Blueprint, jsonify

from ewentts.models import Event
from ewentts.utils import requires_auth, return_jsonified_events, paginate, get_per_page

feed = Blueprint("feed", __name__)


logger = logging.getLogger("feed")


@feed.route("/feed", methods=["GET"])
@requires_auth
def basic_feed():
    """Endpoint which returns feed of events

    Properties:
        event_id: id of event

    Returns:
        200: events, next_page and list_len in json
        204: if no events are available to be returned
        405: if other method then GET used
    """
    logger.info("feed called")
    per_page = get_per_page()
    query = Event.query().order(Event.start_datetime)

    '''
        events = query.fetch()
    id_list = []
    for event in events:
        event.event_id = event.key.id()
        event.put()
        id_list += [event.event_id]
        #id_list += [event.put()]
    print(id_list)

    #id_list = id_list.order(Event._key)
    query = Event.query() 
    query = query.filter(Event.event_id.IN(id_list))

    events = query.fetch()
    print(events)
    return ""
    '''

    events, next_page = paginate(query, per_page)

    if not events:
        logger.warning("no events found")
        return jsonify(""), 204
    logger.info("search finished")
    json = return_jsonified_events(events, next_page=next_page)
    return json
