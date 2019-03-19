import unittest

from ewentts.search.utils import return_next_name
from ewentts.utils import BadRequestError


class TestReturnNextName(unittest.TestCase):
    def test_return_next_name(self):
        self.assertEqual(return_next_name("Name"), "Namf")
        self.assertEqual(return_next_name("Namz"), "Nana")
        self.assertEqual(return_next_name("Zzzz"), None)
        self.assertEqual(return_next_name("N"), "O")

    def test_fails_with_none(self):
        with self.assertRaises(BadRequestError):
            return_next_name(None)

    def test_fails_with_int(self):
        with self.assertRaises(BadRequestError):
            return_next_name(1)


if __name__ == "__main__":
    unittest.main()