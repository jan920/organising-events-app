import sys
import unittest
from datetime import datetime, timedelta

from dateutil.parser import parse
from google.appengine.ext import testbed

from ewentts.events.utils import validate_start_datetime, validate_end_datetime, return_edited_event, create_event

sys.path.append('../')

from ewentts.models import Event, User


class CreateEventTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(overwrite=True)
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.user1 = User(user_names=["User", "Name"],
                          id="ab11",
                          profile_picture_url="https://c1.staticflickr.com/2/1520/24330829813_944c817720_b.jpg",
                          user_email="email")
        self.user1.put()
        self.body1 = {"event_name": "Name",
                      "start_datetime": "2100-12-25T07:45:53 GMT",
                      "location": [0.0, 0.0],
                      "event_picture_url": "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png",
                      "private": False}

        self.body2 = {"event_name": "Name2",
                      "start_datetime": "2098-12-25T07:45:53 GMT",
                      "end_datetime": "2098-12-30T17:45:53+10:00",
                      "location": [10.0, 10.0],
                      "event_picture_url": "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti.jpg",
                      "description": "This is description",
                      "private": True}

    def tearDown(self):
        self.testbed.deactivate()

    def test_create_event(self):

        event1 = create_event(self.body1, self.user1.key.id())
        event2 = create_event(self.body2, self.user1.key.id())

        self.assertEqual(event1.event_name, "Name")
        self.assertEqual(event1.status, "future")
        self.assertEqual(event1.start_datetime, parse("2100-12-25T07:45:53"))
        self.assertEqual(event1.end_datetime, parse("2100-12-26T07:45:53"))
        self.assertEqual(event1.latitude, 0.0)
        self.assertEqual(event1.longitude, 0.0)
        self.assertEqual(event1.event_picture_url, "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png")
        self.assertEqual(event1.private, False)

        self.assertEqual(event2.event_name, "Name2")
        self.assertEqual(event1.status, "future")
        self.assertEqual(event2.start_datetime, parse("2098-12-25T07:45:53"))
        self.assertEqual(event2.end_datetime, parse("2098-12-30T07:45:53"))
        self.assertEqual(event2.latitude, 10.0)
        self.assertEqual(event2.longitude, 10.0)
        self.assertEqual(event2.event_picture_url, "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti.jpg")
        self.assertEqual(event2.description, "This is description")
        self.assertEqual(event2.private, True)

    def test_create_event_wrong_datetime_values(self):
        self.body1["start_datetime"] = "2098-12-25T07:45:53"
        self.body2["end_datetime"] = "2080-12-25T07:45:53 GTM"

        with self.assertRaises(Exception):
            create_event(self.body1, self.user1.key.id())
        with self.assertRaises(Exception):
            create_event(self.body2, self.user1.key.id())

    def test_create_event_wrong_picture_values(self):
        self.body1["event_picture_url"] = "picture.jpg"
        self.body2["event_picture_url"] = "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti"

        with self.assertRaises(Exception):
            create_event(self.body1, self.user1.key.id())
        with self.assertRaises(Exception):
            create_event(self.body2, self.user1.key.id())

    def test_create_event_wrong_location_values(self):
        self.body1["location"] = [100, 10]
        self.body2["location"] = [10, 200]

        with self.assertRaises(Exception):
            create_event(self.body1, self.user1.key.id())
        with self.assertRaises(Exception):
            create_event(self.body2, self.user1.key.id())


class ReturnEditedEventTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(overwrite=True)
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.user = User(user_names=["User", "Name"],
                         id="ab11",
                         profile_picture_url="https://c1.staticflickr.com/2/1520/24330829813_944c817720_b.jpg",
                         user_email="email")

        self.event1 = Event(event_name = "Event Name",
                            status="future",
                            start_datetime = parse("2100-10-03T10:17:30"),
                            end_datetime=parse("2100-10-06T10:17:30"),
                            latitude=49.395470,
                            longitude=15.590950,
                            event_picture_url = "https://i.imgur.com/nqTGipe.jpg",
                            private = True,
                            organiser = self.user.key)

        self.event2 = Event(event_name = "Event Name2",
                            status="future",
                            start_datetime = parse("2090-10-03T10:17:30"),
                            end_datetime=parse("2090-10-06T10:17:30"),
                            latitude=-49.395470,
                            longitude=-15.590950,
                            event_picture_url = "https://i.imgur.com/nqTGipe.jpg",
                            description = "description",
                            private = True,
                            organiser=self.user.key)

    def tearDown(self):
        self.testbed.deactivate()

    def test_change_event_name(self):
        body1 = {"event_name": "New Event Name"}
        body2 = {"event_name": "Another new event name"}

        self.event1 = return_edited_event(self.event1, body1)
        self.event2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.event_name, "New Event Name")
        self.assertEqual(self.event2.event_name, "Another new event name")

    def test_change_start_datetime(self):
        body1 = {"start_datetime": "2100-10-02T07:45:53+01:00"}
        body2 = {"start_datetime": "2090-09-30T07:45:53 UTC"}

        self.user1 = return_edited_event(self.event1, body1)
        self.user2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.start_datetime, parse("2100-10-02T06:45:53"))
        self.assertEqual(self.event2.start_datetime, parse("2090-09-30T07:45:53"))

    def test_change_start_datetime_invalid_datetime(self):
        body1 = {"start_datetime": "2000-12-25T07:45:53+01:00"}
        body2 = {"start_datetime": "2100-12-25T07:45:53"}
        body3 = {"start_datetime": "2050-12-25T07:45:53"}

        with self.assertRaises(Exception):
            return_edited_event(self.event1, body1)
        with self.assertRaises(Exception):
            return_edited_event(self.event1, body2)
        with self.assertRaises(Exception):
            return_edited_event(self.event1, body3)

    def test_change_end_datetime(self):
        body1 = {"end_datetime": "2100-10-08T11:45:53+01:00"}
        body2 = {"end_datetime": "2090-10-03T11:45:53 UTC"}

        self.user1 = return_edited_event(self.event1, body1)
        self.user2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.end_datetime, parse("2100-10-08T10:45:53"))
        self.assertEqual(self.event2.end_datetime, parse("2090-10-03T11:45:53"))

    def test_change_end_datetime_invalid_datetime(self):
        body1 = {"end_datetime": "2080-12-25T07:45:53+01:00"}
        body2 = {"end_datetime": "2100-12-25T07:45:53"}
        body3 = {"end_datetime": "2200-12-25T07:45:53"}

        with self.assertRaises(Exception):
            return_edited_event(self.event1, body1)
        with self.assertRaises(Exception):
            return_edited_event(self.event1, body2)
        with self.assertRaises(Exception):
            return_edited_event(self.event1, body3)

    def test_change_start_datetime_and_end_datetime(self):
        body1 = {"end_datetime": "2100-10-08T11:45:53+01:00",
                 "start_datetime": "2100-10-02T07:45:53+01:00"}
        body2 = {"end_datetime": "2050-10-03T11:45:53 UTC",
                 "start_datetime": "2050-10-02T07:45:53 UTC"}

        self.user1 = return_edited_event(self.event1, body1)
        self.user2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.end_datetime, parse("2100-10-08T10:45:53"))
        self.assertEqual(self.event1.start_datetime, parse("2100-10-02T06:45:53"))
        self.assertEqual(self.event2.end_datetime, parse("2050-10-03T11:45:53"))
        self.assertEqual(self.event2.start_datetime, parse("2050-10-02T07:45:53"))

    def test_change_location(self):
        body1 = {"location": (19.395470, 35.590950)}
        body2 = {"location": (40.395470, 10.590950)}

        self.user1 = return_edited_event(self.event1, body1)
        self.user2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.latitude, 19.395470)
        self.assertEqual(self.event1.longitude, 35.590950)
        self.assertEqual(self.event2.latitude, 40.395470)
        self.assertEqual(self.event2.longitude, 10.590950)

    def test_change_event_picture_url(self):
        body1 = {
            "event_picture_url": "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png"}
        body2 = {"event_picture_url": "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA.jpg"}

        self.user1 = return_edited_event(self.event1, body1)
        self.user2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.event_picture_url,
                         "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png")
        self.assertEqual(self.event2.event_picture_url, "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA.jpg")

    def test_change_event_picture_to_invalid_raises_error(self):
        body1 = {
            "event_picture_url": "blogmedia.evbstatic.com/wp-conts-reach-more-people-eventbrite.png"}
        body2 = {
            "event_picture_url": "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA"}

        with self.assertRaises(Exception):
            return_edited_event(self.event1, body1)
        with self.assertRaises(Exception):
            return_edited_event(self.event1, body2)

    def test_change_description(self):
        body1 = {"description": "New Description"}
        body2 = {"description": "Another new description"}

        self.event1 = return_edited_event(self.event1, body1)
        self.event2 = return_edited_event(self.event2, body2)

        self.assertEqual(self.event1.description, "New Description")
        self.assertEqual(self.event2.description, "Another new description")


class ValidateStartDatetimeTest(unittest.TestCase):
    def test_validate_start_datetime_correct_time(self):
        start_datetime1 = parse("2100-12-25 07:45:53")
        end_datetime1 = parse("2100-12-30 07:45:53")
        start_datetime2 = datetime.utcnow() + timedelta(days=1)
        end_datetime2 = datetime.utcnow() + timedelta(days=2)

        self.assertEqual(validate_start_datetime(start_datetime1, end_datetime1), True)
        self.assertEqual(validate_start_datetime(start_datetime2, end_datetime2), True)

    def test_validate_start_datetime_in_past_raises_error(self):
        end_datetime = parse("2100-12-30 07:45:53")
        start_datetime1 = parse("2000-12-25 07:45:53")
        start_datetime2 = datetime.utcnow()
        start_datetime2 -= timedelta(days=1)

        with self.assertRaises(ValueError):
            validate_start_datetime(start_datetime1, end_datetime)
        with self.assertRaises(ValueError):
            validate_start_datetime(start_datetime2, end_datetime)

    def test_validate_start_datetime_before_end_datetime(self):
        start_datetime = parse("2050-12-25 07:45:53")
        end_datetime = parse("2050-12-25 07:45:53")

        with self.assertRaises(ValueError):
            validate_start_datetime(start_datetime, end_datetime)

    def test_validate_start_datetime_more_then_week_before_end_datetime(self):
        start_datetime = parse("2050-11-25 07:45:53")
        end_datetime = parse("2050-12-25 07:45:53")

        with self.assertRaises(ValueError):
            validate_start_datetime(start_datetime, end_datetime)


class ValidateEndDatetimeTest(unittest.TestCase):
    def test_validate_end_datetime_correct_time(self):
        start_datetime1 = parse("2100-12-20 07:45:53")
        end_datetime1 = parse("2100-12-25 07:45:53")
        start_datetime2 = datetime.utcnow() - timedelta(days=1)
        end_datetime2 = datetime.utcnow() + timedelta(days=1)

        self.assertEqual(validate_end_datetime(end_datetime1, start_datetime1), True)
        self.assertEqual(validate_end_datetime(end_datetime2, start_datetime2), True)

    def test_validate_end_datetime_in_past_raises_error(self):
        start_datetime = parse("2000-10-25 07:45:53")
        end_datetime1 = parse("2000-12-25 07:45:53")
        end_datetime2 = datetime.utcnow()
        end_datetime2 -= timedelta(days=1)

        with self.assertRaises(ValueError):
            validate_end_datetime(end_datetime1, start_datetime)
        with self.assertRaises(ValueError):
            validate_end_datetime(end_datetime2, start_datetime)

    def test_validate_end_datetime_after_start_datetime(self):
        start_datetime = parse("2050-12-25 07:45:53")
        end_datetime = parse("2050-12-25 07:45:53")

        with self.assertRaises(ValueError):
            validate_end_datetime(end_datetime, start_datetime)

    def test_validate_end_datetime_more_then_week_after_start_datetime(self):
        start_datetime = parse("2050-11-25 07:45:53")
        end_datetime = parse("2050-12-25 07:45:53")

        with self.assertRaises(ValueError):
            validate_end_datetime(end_datetime, start_datetime)