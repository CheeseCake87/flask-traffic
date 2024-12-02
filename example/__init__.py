from flask import Flask, render_template

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import CSVStore

log_policy = LogPolicy(
    request_browser=True,
    response_time=True,
    response_size=True,
    response_exception=True,
)

store = CSVStore(log_policy=log_policy)


def create_app() -> Flask:
    app = Flask(__name__)
    Traffic(app, stores=store)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
