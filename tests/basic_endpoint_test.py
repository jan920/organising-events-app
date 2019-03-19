# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
from flask import Response

from ewentts import create_app
import unittest
from flask.testing import FlaskClient


class BasicTestCase(unittest.TestCase):
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
        self.assertEqual(self.client.get('/').status_code, 403)
        self.assertEqual(self.client.get('/home').status_code, 403)
        # users
        #self.assertEqual(self.client.get('/register').status_code, 403)
        # events
        self.assertEqual(self.client.get('/home').status_code, 403)
        # search
        #self.assertEqual(self.client.get('/search/user').status_code, 403)
        #self.assertEqual(self.client.get('/search/event').status_code, 403)
        # feed
        self.assertEqual(self.client.get('/feed').status_code, 403)


    def test_page_does_not_exist(self):
        self.assertEqual(self.client.get('/user/1234').status_code, 404)
        self.assertEqual(self.client.get('/user/1234/edit').status_code, 404)
        self.assertEqual(self.client.get('/event/3221').status_code, 404)
        self.assertEqual(self.client.get('/event/3221/edit').status_code, 404)
        self.assertEqual(self.client.get('/event/3221/post').status_code, 404)


    #test wrong method
"""
