import sys
import sys
import unittest

from google.appengine.ext import testbed

from ewentts.users.utils import validate_email, return_edited_user

sys.path.append('../')

from ewentts.models import User

from exceptions import Exception


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class BadRequest(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class CreateUserTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(overwrite=True)
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_create_user(self):
        pass


class ReturnEditedUserTestCase(unittest.TestCase):
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
        self.user2 = User(user_names=["User", "Name"],
                          id="ab12",
                          profile_picture_url="https://c1.staticflickr.com/2/1520/24330829813_944c817720_b.jpg",
                          user_email="email")

    def tearDown(self):
        self.testbed.deactivate()

    def test_edit_profile_picture_url(self):
        body1 = {
            "profile_picture_url": "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png"}
        body2 = {"profile_picture_url": "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA.jpg"}

        self.user1 = return_edited_user(self.user1, body1)
        self.user2 = return_edited_user(self.user2, body2)

        self.assertEqual(self.user1.profile_picture_url,
                         "https://blogmedia.evbstatic.com/wp-content/uploads/wpmulti/sites/3/2016/05/10105129/discount-codes-reach-more-people-eventbrite.png")
        self.assertEqual(self.user2.profile_picture_url, "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA.jpg")

    def test_non_valid_profile_picture_returns_error(self):
        body1 = {
            "profile_picture_url": "blogmedia.evbstatic.com/wp-conts-reach-more-people-eventbrite.png"}
        body2 = {"profile_picture_url": "https://media.wired.com/photos/598e35fb99d76447c4eb1f28/master/pass/phonepicutres-TA"}

        with self.assertRaises(Exception):
            return_edited_user(self.user1, body1)
        with self.assertRaises(Exception):
            return_edited_user(self.user2, body2)

    def test_edit_user_email(self):
        body1 = {"user_email": "jan@gmail.com"}
        body2 = {"user_email": "test.email@gmail.com"}

        self.user1 = return_edited_user(self.user1, body1)
        self.user2 = return_edited_user(self.user2, body2)

        self.assertEqual(self.user1.user_email, "jan@gmail.com")
        self.assertEqual(self.user2.user_email, "test.email@gmail.com")

    def test_non_valid_email_returns_error(self):
        body1 = {"user_email": "jan@gmail"}
        body2 = {"user_email": "test.emailgmail.com"}

        with self.assertRaises(Exception):
            return_edited_user(self.user1, body1)
        with self.assertRaises(Exception):
            return_edited_user(self.user2, body2)


class ValidateEmailTest(unittest.TestCase):

    def test_validate_email_is_email(self):
        email1 = "abcde@gmail.com"
        email2 = "abcde@seznam.cz"
        email3 = "aafkjff213.ab@gmail.com"

        self.assertEqual(validate_email(email1), True)
        self.assertEqual(validate_email(email2), True)
        self.assertEqual(validate_email(email3), True)

    def test_non_email_str_raises_error(self):
        email1 = "abc"
        email2 = "abcd@gmailcom"
        email3 = "abcd@.com"
        email4 = "@gmail.com"
        email5 = ""
        email6 = "@.com"
        email7 = "@."

        with self.assertRaises(ValueError):
            validate_email(email1)
        with self.assertRaises(ValueError):
            validate_email(email2)
        with self.assertRaises(ValueError):
            validate_email(email3)
        with self.assertRaises(ValueError):
            validate_email(email4)
        with self.assertRaises(ValueError):
            validate_email(email5)
        with self.assertRaises(ValueError):
            validate_email(email6)
        with self.assertRaises(ValueError):
            validate_email(email7)

    def test_other_datatype_raise_error(self):
        email1 = 1
        email2 = None
        email3 = ["gmail", "com"]

        with self.assertRaises(ValueError):
            validate_email(email1)
        with self.assertRaises(ValueError):
            validate_email(email2)
        with self.assertRaises(ValueError):
            validate_email(email3)
