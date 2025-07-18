# flask-traffic 🚦

[![PyPI version](https://img.shields.io/pypi/v/flask-traffic)](https://pypi.org/project/flask-traffic/)
[![License](https://img.shields.io/github/license/CheeseCake87/flask-traffic)](https://raw.githubusercontent.com/CheeseCake87/flask-traffic/master/LICENSE)

Store and monitor site traffic.

```bash
pip install flask-traffic
```

**🚨 Note:**

**SQLStore** requires `sqlalchmey`

```bash
pip install sqlalchemy
# or
pip install "flask-traffic[sqlalchemy]"
```

**SQLORMStore** requires `sqlalchmey` but recommends `flask-sqlalchemy`

```bash
pip install flask-sqlalchemy
# or
pip install "flask-traffic[flask-sqlalchemy]"
```

**RedisStore** requires `redis`

```bash
pip install redis
# or
pip install "flask-traffic[redis]"
```

<!-- TOC -->
* [flask-traffic 🚦](#flask-traffic-)
  * [Minimal Example](#minimal-example)
  * [The `LogPolicy` class](#the-logpolicy-class)
  * [Stores](#stores)
    * [JSONStore](#jsonstore)
    * [CSVStore](#csvstore)
    * [SQLStore](#sqlstore)
    * [SQLORMStore](#sqlormstore)
      * [SQLORMModelMixin](#sqlormmodelmixin)
    * [RedisStore](#redisstore)
  * [Reading store data](#reading-store-data)
  * [Bigger Examples](#bigger-examples)
    * [`SQLORMStore` with Flask-SQLAlchemy, `JSONStore` for exceptions](#sqlormstore-with-flask-sqlalchemy-jsonstore-for-exceptions)
    * [`CSVStore` only IP Addresses](#csvstore-only-ip-addresses)
<!-- TOC -->


## Minimal Example

```python
from flask import Flask
from flask_traffic import Traffic
from flask_traffic.stores import JSONStore

traffic = Traffic()


def create_app():
    app = Flask(__name__)

    json_store = JSONStore()

    traffic.init_app(app, stores=json_store)

    @app.route('/')
    def index():
        return 'Hello, World!'

    @app.route('/traffic')
    def traffic():
        return json_store.read()

    return app
```

`instance/traffic.json`

```text
...
{
"request_date": "2024-12-03T20:10:34.932025",
"request_method": "GET",
"request_path": "/",
"request_remote_address": "127.0.0.1",
"request_referrer": null,
"request_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
"request_browser": null,
"request_platform": null,
"response_time": 1,
"response_size": 13,
"response_status_code": 200,
"response_exception": null,
"response_mimetype": "text/html"
}
...
```

## The `LogPolicy` class

`from flask_traffic import LogPolicy`

The log policy is used to tell Flask-Traffic what data to store after a request is
made in whatever store, or stores you have configured.

A new instance of `LogPolicy` will have all the log attributes set to `True` by
default.

You can use the methods `set_from_true` or `set_from_false` to select which attributes
to store.

`set_from_true` will allow you to disable certain attributes from being stored.

`set_from_false` will allow you to enable certain attributes to be stored.

If a store is created without a log policy passed in, one is created with all log
attributes set to `True`.

`only_on_exception`, and `skip_on_exception` are set to `False`.

`on_endpoints`, `skip_endpoints`, `on_status_codes`, and `skip_status_codes` are
used to scope or skip logging based on the endpoint or status code. These are disabled
by default.

Here's an example of the `LogPolicy` class only storing the date and request path:

```python
from flask_traffic.stores import JSONStore
from flask_traffic import LogPolicy

log_policy = LogPolicy().set_from_false(
    request_date=True,
    request_path=True
)

json_store = JSONStore(log_policy=log_policy)
```

Results in:

```text
...
{
"request_date": "2024-12-03T20:33:43.051597",
"request_path": "/"
}
...
```

Here's an example of the `LogPolicy` class storing everything except the response size:

```python
from flask_traffic.stores import JSONStore
from flask_traffic import LogPolicy

log_policy = LogPolicy().set_from_true(
    response_size=False
)

json_store = JSONStore(log_policy=log_policy)
```

## Stores

### JSONStore

This store saves traffic data in a JSON file. The file is created in the
`instance` folder of the Flask app by default.

### CSVStore

This store saves traffic data in a CSV file. The file is created in the
`instance` folder of the Flask app by default.

### SQLStore

This store saves traffic data in a SQL type database. It defaults to using SQLite
which is created in the `instance` folder of the Flask app by default.

You can specify a database URL, or pass in an already created SQLAlchemy engine.

This store is used if you want to store traffic data in a SQL type database.

### SQLORMStore

This is an ORM version of the `SQLStore`. It is designed to integrate with an existing
SQLAlchemy ORM environment like Flask-SQLAlchemy.

#### SQLORMModelMixin

This mixin is used to set the correct table columns for the `SQLORMStore`.

Example:

```python
from flask_traffic.stores import SQLORMModelMixin

from app import db


class Traffic(db.Model, SQLORMModelMixin):
    pass
```

### RedisStore

This store sends traffic data to a Redis event stream.

## Reading store data

Each store has a `read` method that will return the data in the store as a
list of dictionaries.

Here's an example of reading the data from a `CSVStore`:

```python
@app.route("/read-csv")
def read_csv():
    return csv_store.read()
```

This will return the data as JSON.

You can also override the `read` method to change the default,
or add more methods of course.

here's an example of overriding the `read` method in a `SQLStore` to only return data
where the response status code is 200:

```python
class MyStore(SQLStore):
    def read(self):
        with self.database_engine.connect() as connection:
            results = connection.execute(
                self.database_log_table.select().order_by(
                    self.database_log_table.c.traffic_id.desc()
                ).where(
                    self.database_log_table.c.response_status_code == 200
                )
            )
            return [row._asdict() for row in results.fetchall()]
```

## Bigger Examples

### `SQLORMStore` with Flask-SQLAlchemy, `JSONStore` for exceptions

This example will store traffic data in a SQL database using Flask-SQLAlchemy and
store any traffic that causes exceptions in a JSON file.

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import JSONStore, SQLORMStore, SQLORMModelMixin

db = SQLAlchemy()
traffic = Traffic()


class Cars(db.Model):
    car_id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(80), unique=True, nullable=False)
    model = db.Column(db.String(80), unique=True, nullable=False)


class Traffic(db.Model, SQLORMModelMixin):
    pass


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/db.sqlite'

    db.init_app(app)

    # init traffic after db.init_app to find the db session
    traffic.init_app(
        app, stores=[
            JSONStore(
                log_policy=LogPolicy(only_on_exception=True)
            ),
            SQLORMStore(
                Traffic,
                log_policy=LogPolicy(skip_on_exception=True)
            )
        ])

    @app.route('/')
    def index():
        return 'Hello, World!'

    return app
```

### `CSVStore` only IP Addresses

This example will store traffic data in a CSV file and only store the IP address

```python
from flask import Flask

from flask_traffic import Traffic, LogPolicy
from flask_traffic.stores import CSVStore

traffic = Traffic()


def create_app():
    app = Flask(__name__)

    traffic.init_app(
        app,
        stores=CSVStore(
            log_policy=LogPolicy().set_from_false(request_remote_address=True)
        )
    )

    @app.route('/')
    def index():
        return 'Hello, World!'

    return app
```
