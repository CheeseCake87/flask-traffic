import typing as t
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, Table, Column, String, Integer, DateTime, MetaData

from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic
    from sqlalchemy.engine import Engine


class SQLStore:
    filename: str
    location: t.Optional[t.Union[str, Path]]

    filepath: t.Optional[Path]
    log_policy: LogPolicy

    database_table_name: t.Optional[str]
    database_url: t.Optional[str]
    database_engine: t.Optional["Engine"]
    database_metadata: t.Optional["MetaData"]
    database_log_table: t.Optional["Table"]

    _traffic_instance = None

    def __init__(
        self,
        filename: t.Optional[str] = "traffic.sqlite",
        location: t.Optional[t.Union[str, Path]] = None,
        log_policy: LogPolicy = None,
        *,
        database_table_name: t.Optional[str] = "_traffic_",
        database_url: t.Optional[str] = None,
        database_engine: t.Optional["Engine"] = None,
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

        else:
            self.log_policy = log_policy

        self.database_table_name = database_table_name

        if database_url is not None:
            self.database_url = database_url
            return
        else:
            self.database_url = None

        if database_engine is not None:
            self.database_engine = database_engine
            return
        else:
            self.database_engine = None

        self.filename = filename
        self.location = location

    def _init_database(
        self, url: t.Optional[str] = None, engine: t.Optional["Engine"] = None
    ):
        if url:
            self.database_engine = create_engine(self.database_url)
        elif engine:
            self.database_engine = engine
        else:
            self.database_engine = create_engine(f"sqlite:///{self.filepath}")

        self.database_metadata = MetaData()
        self.database_log_table = Table(
            self.database_table_name,
            self.database_metadata,
            Column("traffic_id", Integer, primary_key=True),
            Column("request_date", DateTime, nullable=True),
            Column("request_method", String, nullable=True),
            Column("request_path", String, nullable=True),
            Column("request_remote_address", String, nullable=True),
            Column("request_referrer", String, nullable=True),
            Column("request_user_agent", String, nullable=True),
            Column("request_browser", String, nullable=True),
            Column("request_platform", String, nullable=True),
            Column("response_time", Integer, nullable=True),
            Column("response_size", String, nullable=True),
            Column("response_status_code", Integer, nullable=True),
            Column("response_exception", String, nullable=True),
            Column("response_mimetype", String, nullable=True),
        )

    def _build_database_filepath(self, traffic_instance: "Traffic"):
        if self.location is None:
            self.filepath = traffic_instance.app_instance_folder / self.filename
        else:
            if isinstance(self.location, str):
                self.filepath = Path(self.location) / self.filename

            if isinstance(self.location, Path):
                self.filepath = self.location / self.filename

    def setup(self, traffic_instance: "Traffic") -> None:
        if self.database_url:
            self._init_database(url=self.database_url)

        elif self.database_engine:
            self._init_database(engine=self.database_engine)

        else:
            self._build_database_filepath(traffic_instance)
            self._init_database()

        self.database_metadata.create_all(self.database_engine)

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
                if isinstance(locals()[attr], datetime):
                    data[attr] = locals()[attr].isoformat()
                    continue

                data[attr] = locals()[attr]

            else:
                data[attr] = None

        with self.database_engine.connect() as connection:
            connection.execute(self.database_log_table.insert().values(data))
            connection.commit()
