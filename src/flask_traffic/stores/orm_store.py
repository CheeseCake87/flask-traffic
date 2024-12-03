import typing as t
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import insert

from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic
    from sqlalchemy.orm import Session
    from sqlalchemy.sql._typing import _DMLTableArgument


class ORMTrafficMixin:
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


class ORMStore:
    db_session: t.Optional["Session"]
    model: "_DMLTableArgument"

    def __init__(
        self,
        model: "_DMLTableArgument",
        db_session: t.Optional["Session"] = None,
        log_policy: LogPolicy = None,
    ) -> None:
        if log_policy is None:
            from .._log_policy import LogPolicy

            self.log_policy = LogPolicy(
                response_time=True,
                request_date=True,
                request_method=True,
                response_size=True,
                response_status_code=True,
                request_path=True,
                request_user_agent=True,
                request_remote_address=True,
                response_exception=True,
                request_referrer=True,
                request_browser=True,
                request_platform=True,
                response_mimetype=True,
            )

        self.model = model
        self.db_session = db_session

    def setup(self, traffic_instance: "Traffic") -> None:
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
    ):
        data = {}

        for attr, attr_val in self.log_policy.__dict__.items():
            if attr == "log_only_on_exception":
                continue

            if attr_val:
                data[attr] = locals()[attr]

            else:
                data[attr] = None

        self.db_session.execute(insert(self.model).values(data))
        self.db_session.commit()
