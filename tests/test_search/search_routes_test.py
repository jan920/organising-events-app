import unittest

from ewentts import create_app


class TestSearchUsersEndpoint(unittest.TestCase):
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
        self.assertEqual(self.client.get('/search/user').status_code, 403)


class TestSearchEventsByNamesEndpoint(unittest.TestCase):
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
        self.assertEqual(self.client.get('/search/events/names/').status_code, 403)


class TestSearchEventEndpoint(unittest.TestCase):
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
        self.assertEqual(self.client.get('/search/events/').status_code, 403)
