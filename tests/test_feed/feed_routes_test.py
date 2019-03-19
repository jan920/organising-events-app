import unittest

from ewentts import create_app


class TestFeedEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global app
        app = create_app()
        app.Testing = True

    def setUp(self):
        self.client = app.test_client()
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer your_token'

    def tearDown(self):
        pass

    def testUnauthorizedResponse(self):
        # main
        self.assertEqual(self.client.get('/feed').status_code, 403)