from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

from flask import Flask
import firebase_admin
from firebase_admin import credentials


def create_app():
	"""Return Created app"""
	app = Flask(__name__)
	cred = credentials.Certificate('ewenttsapp-firebase-adminsdk-ikh1d-9f2e8e24ad.json')
	try:
		default_app = firebase_admin.initialize_app(cred)
	except:
		pass
	from ewentts.main.routes import main
	from ewentts.users.routes import users
	from ewentts.events.routes import events
	from ewentts.posts.routes import posts
	from ewentts.search.routes import search
	from ewentts.feed.routes import feed
	from ewentts.errors.handlers import errors
	from ewentts.datastore_generator.generator import generator
	app.register_blueprint(main)
	app.register_blueprint(users)
	app.register_blueprint(events)
	app.register_blueprint(posts)
	app.register_blueprint(search)
	app.register_blueprint(feed)
	app.register_blueprint(errors)
	app.register_blueprint(generator)

	return app


