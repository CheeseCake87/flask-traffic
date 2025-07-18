from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import JSONStore, CSVStore, SQLStore, SQLORMStore, \
    SQLORMModelMixin, RedisStore

# create an instance of the flask_sqlalchemy extension
db = SQLAlchemy()

traffic = Traffic()


# this model is for the SQLORMStore set below
class ModelModel(db.Model, SQLORMModelMixin):
    pass


# create a log policy to pass the stores.
# This is used to disable all, then enable what you want.
log_policy = LogPolicy(
    skip_endpoints=("static",),
    skip_on_exception=True,
    max_request_path_length=100,
).set_from_false(
    request_date=True,
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
    request_host_url=True,
    request_path=True,
    response_exception=True,
    response_time=True,
)

# create a csv file store
csv_store = CSVStore(log_policy=log_policy)

# create a sqlite store
sql_store = SQLStore(log_policy=log_policy)

# create a JSON store
json_store = JSONStore(log_policy=log_policy)

# create an ORM store and pass the above model
sqlorm_store = SQLORMStore(model=ModelModel)

# create a JSON store
json_exception_store = JSONStore(
    filename="exception.json", log_policy=only_on_exception)

# This example is configure to connect to a docker instance of redis
redis_store = RedisStore(
    redis_host="localhost",
    event_name="traffic",
    redis_port=8001,
    log_policy=log_policy,
)


# create a custom store and override the read method
class MyStore(JSONStore):
    def read(self):
        return "This is a custom store"


store_read_override = MyStore(filename="custom.json", log_policy=log_policy)


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///traffic_orm.sqlite"
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # place the traffic extension below the db.init_app(app) line,
    # this will pick up th db.session automatically from db.init_app(app)
    # traffic.init_app(app, stores=[json_store, csv_store, sqlite_store, orm_store])

    traffic.init_app(app, stores=[
        csv_store,
        json_store,
        sql_store,
        sqlorm_store,
        redis_store,
        json_exception_store,
        store_read_override
    ])

    # You can add multiple stores at once, and they will all log data
    # based on the log policy

    @app.route("/")
    def index():
        return render_template("index.html")

    # This will create an exemption, and be stored in the json_exception_store
    @app.route("/exception")
    def exception():
        return render_template("exception.html")

    #
    # Reading will always be one behind, as the log is written after the request

    @app.route("/read-csv")
    def read_csv():
        return csv_store.read()

    @app.route("/read-json")
    def read_json():
        return json_store.read()

    @app.route("/read-sql")
    def read_sql():
        return sql_store.read()

    @app.route("/read-orm")
    def read_orm():
        return sqlorm_store.read()

    @app.route("/read-redis")
    def read_redis():
        return redis_store.read()

    @app.route("/read-custom")
    def read_custom():
        return store_read_override.read()

    @app.route("/read-exceptions")
    def read_exceptions():
        return json_exception_store.read()

    return app
