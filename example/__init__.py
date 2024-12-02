from flask import Flask, render_template

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import JSONStore

log_policy = LogPolicy(
    request_browser=True,
    response_time=True,
    response_size=True,
    response_exception=True,
)

json_store = JSONStore()


def create_app() -> Flask:
    app = Flask(__name__)
    Traffic(app, stores=json_store)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
