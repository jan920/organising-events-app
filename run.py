import logging

from ewentts import create_app

logger = logging.getLogger('run')


app = create_app()

logger.info("app created")

if __name__ == "__main__":
    app.run(debug=True)
