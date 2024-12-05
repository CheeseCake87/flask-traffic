from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import JSONStore, SQLStore, SQLORMModelMixin

# create an instance of the flask_sqlalchemy extension
db = SQLAlchemy()

traffic = Traffic()

# create a log policy to pass the stores.
# This is used to disable all, then enable what you want.
log_policy = LogPolicy(
    skip_endpoints=("static",),
    skip_on_exception=True,
).set_from_false(
    request_browser=True,
    response_time=True,
    response_size=True,
    response_status_code=True,
    request_path=True,
)

only_on_exception = LogPolicy(
    only_on_exception=True,
).set_from_false(
    request_date=True,
    request_path=True,
    response_exception=True,
    response_time=True,
)

# create a csv file store
# csv_store = CSVStore(log_policy=log_policy)

# create a sqlite store
# sqlite_store = SQLStore(log_policy=log_policy)
sqlite_store = SQLStore(log_policy=log_policy)


# create a JSON store
json_store = JSONStore(log_policy=only_on_exception)


# create an ORM store that links to the flask_sqlalchemy extension
class ModelModel(db.Model, SQLORMModelMixin):
    pass


# create an ORM store and pass the above model
# orm_store = SQLORMStore(model=ModelModel)


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///traffic_orm.sqlite"
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # place the traffic extension below the db.init_app(app) line,
    # this will pick up th db.session automatically from db.init_app(app)
    # traffic.init_app(app, stores=[json_store, csv_store, sqlite_store, orm_store])
    traffic.init_app(app, stores=[sqlite_store])

    # You can add multiple stores at once, and they will all log data
    # based on the log policy

    @app.route("/")
    def index():
        return render_template("index.html")

    # This will create an exemption, and be stored in the json_store
    @app.route("/")
    def index1():
        return render_template("index1.html")

    return app
