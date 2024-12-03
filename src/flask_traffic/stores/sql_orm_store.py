import typing as t
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import insert

from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic
    from sqlalchemy.orm import Session
    from sqlalchemy.sql._typing import _DMLTableArgument


class SQLORMModelMixin:
    """
    A mixin for use with ORM SQLAlchemy / Flask-SQLAlchemy models.

    Change the table name by setting the __tablename__ attribute
    in your model, if needed.

    Do not change the column names or types, as these are used
    by flask-traffic internally.

    *Flask-SQLAlchemy example:*

    ::

        class MyTrafficModel(db.Model, SQLORMModelMixin):
            __tablename__ = "my_traffic_table"

    *Defaults:*

    ::

        __tablename__ = "_traffic_"
        traffic_id = Column(Integer, primary_key=True)
        request_date = Column(DateTime, nullable=True)
        request_method = Column(String, nullable=True)
        request_path = Column(String, nullable=True)
        request_remote_address = Column(String, nullable=True)
        request_referrer = Column(String, nullable=True)
        request_user_agent = Column(String, nullable=True)
        request_browser = Column(String, nullable=True)
        request_platform = Column(String, nullable=True)
        response_time = Column(Integer, nullable=True)
        response_size = Column(String, nullable=True)
        response_status_code = Column(Integer, nullable=True)
        response_exception = Column(String, nullable=True)
        response_mimetype = Column(String, nullable=True)

    """
    __tablename__ = "_traffic_"
    traffic_id = Column(Integer, primary_key=True)
    request_date = Column(DateTime, nullable=True)
    request_method = Column(String, nullable=True)
    request_path = Column(String, nullable=True)
    request_remote_address = Column(String, nullable=True)
    request_referrer = Column(String, nullable=True)
    request_user_agent = Column(String, nullable=True)
    request_browser = Column(String, nullable=True)
    request_platform = Column(String, nullable=True)
    response_time = Column(Integer, nullable=True)
    response_size = Column(String, nullable=True)
    response_status_code = Column(Integer, nullable=True)
    response_exception = Column(String, nullable=True)
    response_mimetype = Column(String, nullable=True)


class SQLORMStore:
    db_session: t.Optional["Session"]
    model: "_DMLTableArgument"

    def __repr__(self) -> str:
        return f"<SQLORMStore model={self.model.__name__} log_policy={self.log_policy}>"

    def __init__(
        self,
        model: "_DMLTableArgument",
        db_session: t.Optional["Session"] = None,
        log_policy: LogPolicy = None,
    ) -> None:
        """
        Create a new SQLORMStore instance.

        :param model: the SQLAlchemy model to insert logs into
        :param db_session: the SQLAlchemy session to use (this is automatically set if using Flask-SQLAlchemy)
        :param log_policy: the log policy to use (defaults to log everything if not provided)
        """
        if log_policy is None:
            from .._log_policy import LogPolicy

            self.log_policy = LogPolicy()

        self.model = model
        self.db_session = db_session

    def setup(self, traffic_instance: "Traffic") -> None:
        """
        Set up the SQLORMStore instance.

        :param traffic_instance:
        :return:
        """
        if self.model is None:
            raise ValueError("No model was passed in. ORMStore(..., model: Model)")

        if self.db_session is None:
            if traffic_instance.app.extensions.get("sqlalchemy") is None:
                raise ImportError(
                    "No SQLAlchemy session was found or passed in. "
                    "ORMStore(..., db_session=session)"
                )
            try:
                self.db_session = traffic_instance.app.extensions["sqlalchemy"].session
            except KeyError:
                raise ImportError(
                    "No SQLAlchemy session was found or passed in. "
                    "ORMStore(..., db_session=session)"
                )

    def log(
        self,
        request_date: t.Optional[datetime] = None,
        request_method: t.Optional[str] = None,
        request_path: t.Optional[str] = None,
        request_remote_address: t.Optional[str] = None,
        request_referrer: t.Optional[str] = None,
        request_user_agent: t.Optional[str] = None,
        request_browser: t.Optional[str] = None,
        request_platform: t.Optional[str] = None,
        response_time: t.Optional[int] = None,
        response_size: t.Optional[str] = None,
        response_status_code: t.Optional[int] = None,
        response_exception: t.Optional[str] = None,
        response_mimetype: t.Optional[str] = None,
    ) -> None:
        """
        Log the traffic data.

        :param request_date: the date and time of the request
        :param request_method: the HTTP method of the request
        :param request_path: the path of the request
        :param request_remote_address: the remote address of the request
        :param request_referrer: the referrer of the request
        :param request_user_agent: the user agent of the request
        :param request_browser: the browser of the request (if able to be determined)
        :param request_platform: the platform of the request (if able to be determined)
        :param response_time: the amount of time it took to respond to the request
        :param response_size: the size of the response
        :param response_status_code: the status code of the response
        :param response_exception: the exception that occurred (if any)
        :param response_mimetype: the mimetype of the response
        :return:
        """
        data = {}

        for attr, attr_val in self.log_policy.__dict__.items():
            if attr == "skip_log_on_exception":
                continue

            if attr == "log_only_on_exception":
                continue

            if attr_val:
                data[attr] = locals()[attr]

            else:
                data[attr] = None

        self.db_session.execute(insert(self.model).values(data))
        self.db_session.commit()
