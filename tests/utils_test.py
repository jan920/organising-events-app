import unittest

from dateutil.parser import parse
from google.appengine.ext import testbed

from ewentts.models import Event, User
from ewentts.utils import validate_picture_url, return_event, return_user, validate_location


class RequestDecodedTokenTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class RequestUIDTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class ValidatePictureUrlTest(unittest.TestCase):
    def test_validate_string_is_picture(self):
        picture_url1 = "https://c1.staticflickr.com/2/1520/24330829813_944c817720_b.jpg"
        picture_url2 = "https://www.gettyimages.ie/gi-resources/images/Homepage/Hero/UK/CMS_Creative_164657191_Kingfisher.jpg"
        picture_url3 = "https://cdn.pixabay.com/photo/2016/06/18/17/42/image-1465348_960_720.jpg"
        picture_url4 = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"

        self.assertEqual(validate_picture_url(picture_url1), True)
        self.assertEqual(validate_picture_url(picture_url2), True)
        self.assertEqual(validate_picture_url(picture_url3), True)
        self.assertEqual(validate_picture_url(picture_url4), True)

    def test_non_picture_str_raises_error(self):
        picture_url1 = "abc"
        picture_url2 = "www.picture.cz"
        picture_url3 = "picture.img"
        picture_url4 = ".img"
        picture_url5 = "www.picture.cz/1234.img/123"

        with self.assertRaises(ValueError):
            validate_picture_url(picture_url1)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url2)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url3)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url4)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url5)

    def test_other_datatype_raise_error(self):
        picture_url1 = 1
        picture_url2 = None
        picture_url3 = ["picture", "img"]

        with self.assertRaises(ValueError):
            validate_picture_url(picture_url1)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url2)
        with self.assertRaises(ValueError):
            validate_picture_url(picture_url3)


class ReturnEventTestCase(unittest.TestCase):
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

        self.event1 = Event(event_name="Event Name",
                            status="future",
                            start_datetime=parse("2100-10-03T10:17:30"),
                            end_datetime=parse("2100-11-04T10:17:30"),
                            latitude=49.395470,
                            longitude=15.590950,
                            event_picture_url="https://i.imgur.com/nqTGipe.jpg",
                            private = True,
                            organiser = self.user.key)

        self.event1.put()

    def tearDown(self):
        self.testbed.deactivate()

    def test_return_event_woks(self):
        event = return_event(self.event1.key.id())
        self.assertEqual(event, self.event1)

    def test_return_fails_wrong_id(self):
        with self.assertRaises(Exception):
            return_event(9887)


class ReturnUserTestCase(unittest.TestCase):
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

        self.user.put()

    def tearDown(self):
        self.testbed.deactivate()

    def test_return_user_woks(self):
        user = return_user(self.user.key.id())

        self.assertEqual(user, self.user)

    def test_return_user_wrong_id(self):
        with self.assertRaises(Exception):
            return_user("9885")


class ValidateLocationTest(unittest.TestCase):
    def test_validate_tuple_is_location(self):
        location1 = [0, 0]
        location2 = [90, 180]
        location3 = [-90, -180]
        location4 = [-90, 180]
        location5 = [-40, 20]

        self.assertEqual(validate_location(*location1), True)
        self.assertEqual(validate_location(*location2), True)
        self.assertEqual(validate_location(*location3), True)
        self.assertEqual(validate_location(*location4), True)
        self.assertEqual(validate_location(*location5), True)

    def test_wrong_location_raises_error(self):
        location1 = [0, 181]
        location2 = [90, -181]
        location3 = [-91, -180]
        location4 = [91, 180]
        location5 = [1000, 20]
        location6 = [100, 200]

        with self.assertRaises(ValueError):
            validate_location(*location1)
        with self.assertRaises(ValueError):
            validate_location(*location2)
        with self.assertRaises(ValueError):
            validate_location(*location3)
        with self.assertRaises(ValueError):
            validate_location(*location4)
        with self.assertRaises(ValueError):
            validate_location(*location5)
        with self.assertRaises(ValueError):
            validate_location(*location6)

    def test_other_datatype_raise_error(self):
        location1 = 1
        location2 = None
        location3 = ["picture", "img"]
        location4 = ["10", "10"]

        with self.assertRaises(Exception):
            validate_location(*location1)
        with self.assertRaises(Exception):
            validate_location(*location2)
        with self.assertRaises(Exception):
            validate_location(*location3)
        with self.assertRaises(Exception):
            validate_location(*location4)