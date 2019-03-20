
"""Module containing Classes used in ewentts package

Module contains following classes:
    User
    DeletedUser
    Event
    Post

"""

from google.appengine.ext import ndb


class User(ndb.Model):
    """Class storing users which inherits from ndb.Model

    User class which is used for saving users to the databased

    Attributes:
        user_names (ndb.StringProperty): list of user names
        profile_picture_url (ndb.StringProperty): string containing url link to user's profile picture
        user_email (ndb.StringProperty): string containing user's email address
        followers (ndb.KeyProperty): list of keys of users who follow user
        following (ndb.KeyProperty): list of keys of users who the user follows
        organised_events (ndb.KeyProperty): list of keys of events user organises
        attending_events (ndb.KeyProperty): list of keys of events user is attending
        declined_events (ndb.KeyProperty): list of keys of events user declined
        visited_events (ndb.KeyProperty): list of keys of events user visited

    """
    user_names = ndb.StringProperty(repeated=True)
    profile_picture_url = ndb.StringProperty(indexed=False)
    user_email = ndb.StringProperty(required=True)
    followers = ndb.KeyProperty(kind="User", repeated=True)
    following = ndb.KeyProperty(kind="User", repeated=True)
    organised_events = ndb.KeyProperty(kind="Event", repeated=True)
    attending_events = ndb.KeyProperty(kind="Event", repeated=True)
    declined_events = ndb.KeyProperty(kind="Event", repeated=True)
    visited_events = ndb.KeyProperty(kind="Event", repeated=True)

    def __repr__(self):
        return "User name: %s User email: %s" % (" ".join(self.user_names), str(self.user_email))

    def __hash__(self):
        return hash(self.key.id())


class DeletedUser(ndb.Model):
    """Class storing deleted users which inherits from ndb.Model

    Class which is used for saving deleted users to the databased

    Attributes:
        user_names (ndb.StringProperty): list of user names
        profile_picture_url (ndb.StringProperty): strings containing url link to user's profile picture
        user_email (ndb.StringProperty): string containing user's email address
        followers (ndb.KeyProperty): list of keys of users who follow user
        following (ndb.KeyProperty): list of keys of users who the user follows
        organised_events (ndb.KeyProperty): list of keys of events user organises
        attending_events (ndb.KeyProperty): list of keys of events user is attending
        declined_events (ndb.KeyProperty): list of keys of events user declined
        visited_events (ndb.KeyProperty): list of keys of events user visited

    """
    user_names = ndb.StringProperty(repeated=True)
    profile_picture_url = ndb.StringProperty(indexed=False)
    user_email = ndb.StringProperty(required=True)
    followers = ndb.KeyProperty(kind="User", repeated=True)
    following = ndb.KeyProperty(kind="User", repeated=True)
    organised_events = ndb.KeyProperty(kind="Event", repeated=True)
    attending_events = ndb.KeyProperty(kind="Event", repeated=True)
    declined_events = ndb.KeyProperty(kind="Event", repeated=True)
    visited_events = ndb.KeyProperty(kind="Event", repeated=True)

    def __repr__(self):
        return "User name: %s User email: %s" % (" ".join(self.user_names), str(self.user_email))

    def __hash__(self):
        return hash(self.key.id())


class Event(ndb.Model):
    """Class storing events which inherits from ndb.Model

    Class which is used for saving deleted users to the databased

    Attributes:
        event_name (ndb.StringProperty): string containing event name
        status (ndb.StringProperty): strings containing status of the event past|present|future
        start_datetime (ndb.DateTimeProperty): datetime containing start datetime of the event
        end_datetime (ndb.DateTimeProperty): datetime containing end datetime of the event
        latitude (ndb.FloatProperty): float containing latitude position of the event
        longitude (ndb.FloatProperty): float containing latitude position of the event
        location (ndb.GeoPtProperty): containing tuple containing two floates signifiing gps location of the event
        event_picture_url (ndb.StringProperty): string containing url link to event picture
        description (ndb.StringProperty): str containig description of the event
        private (ndb.BooleanProperty): True if event private False otherwise
        organiser (ndb.KeyProperty): key of user who is the organiser of the event
        guest_list (ndb.KeyProperty): list of user keys who are on the guest list of the event
        attendees (ndb.KeyProperty): list of user keys who are attending the event
        showed_up (ndb.KeyProperty): list of user keys who are came the event
        left (ndb.KeyProperty): list of user keys who left the event
        posts (ndb.KeyProperty): list of post keys which are posted on the event

    """
    event_name = ndb.StringProperty(required=True)
    status = ndb.StringProperty(required=True)
    start_datetime = ndb.DateTimeProperty(required=True)
    end_datetime = ndb.DateTimeProperty(indexed=False)
    latitude = ndb.FloatProperty(required=True)
    longitude = ndb.FloatProperty(required=True)
    location = ndb.GeoPtProperty()
    event_picture_url = ndb.StringProperty(default="https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3"
                                                   "/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png")
    description = ndb.StringProperty(default="", indexed=False)
    private = ndb.BooleanProperty(required=True)
    organiser = ndb.KeyProperty(kind=User, required=True)
    guest_list = ndb.KeyProperty(kind=User, repeated=True)
    attendees = ndb.KeyProperty(kind=User, repeated=True)
    showed_up = ndb.KeyProperty(kind=User, repeated=True)
    left = ndb.KeyProperty(kind=User, repeated=True)
    posts = ndb.KeyProperty(kind="Post", repeated=True)

    def __repr__(self):
        return "Event name: %s Start time: %s" % (self.event_name, str(self.start_datetime))

    def __hash__(self):
        return self.key.id()


class Post(ndb.Model):
    """Class storing posts which inherits from ndb.Model

    Class which is used for saving posts posted to event to the databased

    Attributes:
        creator (ndb.KeyProperty): key of user who is the creator of the post
        post_datetime (ndb.DateTimeProperty): datetime signifying when post was created
        content (ndb.StringProperty): string containing content of the post


    """
    creator = ndb.KeyProperty(kind=User, required=True)
    post_datetime = ndb.DateTimeProperty(required=True, auto_now_add=True)
    content = ndb.StringProperty(required=True, indexed=False)

    def __repr__(self):
        return self.content
