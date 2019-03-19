from google.appengine.ext import ndb


class User(ndb.Model):
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
    creator = ndb.KeyProperty(kind=User, required=True)
    post_datetime = ndb.DateTimeProperty(required=True, auto_now_add=True)
    content = ndb.StringProperty(required=True, indexed=False)

    def __repr__(self):
        return self.content
