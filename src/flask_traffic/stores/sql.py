import typing as t
from datetime import datetime
from pathlib import Path

from .._helpers import prevent_long_paths

try:
    from sqlalchemy import (
        create_engine,
        Table,
        Column,
        String,
        Integer,
        DateTime,
        MetaData,
        BigInteger,
    )
    from sqlalchemy.dialects import postgresql, mysql, sqlite
except ImportError:
    raise ImportError(
        "You're attempting to use a SQLStore but sqlalchemy is not installed. "
        "Please install it with `pip install sqlalchemy`"
    )

from .._globals import IGNORE_LOCALS
from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic
    from sqlalchemy.engine import Engine


BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), "postgresql")
BigIntegerType = BigIntegerType.with_variant(mysql.BIGINT(), "mysql")
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), "sqlite")


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

    def __repr__(self) -> str:
        if self.database_url:
            return f"<SQLStore database_url={self.database_url} log_policy={self.log_policy}>"

        if self.database_engine:
            return f"<SQLStore database_engine={self.database_engine} log_policy={self.log_policy}>"

        return f"<SQLStore filename={self.filepath} log_policy={self.log_policy}>"

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
        """
        Create a new SQLStore instance.

        :param filename: the name of a SQLite database file (skipped if database_url or database_engine is provided)
        :param location: the location of the SQLite database file  (skipped if database_url or database_engine is provided)
        :param log_policy: the log policy to use (defaults to log everything if not provided)
        :param database_table_name: the name of the table to store the traffic data in
        :param database_url: the URL of the database to connect to
        :param database_engine: the SQLAlchemy engine to use (skipped if database_url is provided)
        """
        if log_policy is None:
            from .._log_policy import LogPolicy

            self.log_policy = LogPolicy()

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

    def _build_database_filepath(self, traffic_instance: "Traffic") -> None:
        """
        If database is determined to be a SQLite database, build the filepath.

        :param traffic_instance:
        :return:
        """
        if self.location is None:
            self.filepath = traffic_instance.app_instance_folder / self.filename
        else:
            if isinstance(self.location, str):
                self.filepath = Path(self.location) / self.filename

            if isinstance(self.location, Path):
                self.filepath = self.location / self.filename

    def _init_database(
        self, url: t.Optional[str] = None, engine: t.Optional["Engine"] = None
    ) -> None:
        """
        Initialize the database connection and create the table.

        :param url:
        :param engine:
        :return:
        """
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
            Column("traffic_id", BigIntegerType, primary_key=True),
            Column("request_date", DateTime, nullable=True),
            Column("request_method", String, nullable=True),
            Column("request_host_url", String, nullable=True),
            Column("request_path", String, nullable=True),
            Column("request_endpoint", String, nullable=True),
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

    def setup(self, traffic_instance: "Traffic") -> None:
        """
        Set up the SQLStore instance.

        :param traffic_instance:
        :return:
        """
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
        request_host_url: t.Optional[str] = None,
        request_path: t.Optional[str] = None,
        request_endpoint: t.Optional[str] = None,
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
        :param request_host_url: the host URL of the request
        :param request_path: the path of the request
        :param request_endpoint: the matched endpoint of the request
        :param request_remote_address: the remote address of the request
        :param request_referrer: the referrer of the request
        :param request_user_agent: the user agent of the request
        :param request_browser: the browser of the request (if able to be determined)
        :param request_platform: the platform of the request (if able to be determined)
        :param response_time: the amount of time in milliseconds it took to respond to the request
        :param response_size: the size of the response
        :param response_status_code: the status code of the response
        :param response_exception: the exception that occurred (if any)
        :param response_mimetype: the mimetype of the response
        :return:
        """
        data = {}

        for attr, attr_val in self.log_policy.__dict__.items():
            if attr in IGNORE_LOCALS:
                continue

            if attr_val:
                # Prevent long paths from being stored
                if attr == "request_path":
                    data[attr] = prevent_long_paths(
                        request_path, self.log_policy.max_request_path_length
                    )
                    continue

                data[attr] = locals()[attr]

            else:
                data[attr] = None

        with self.database_engine.connect() as connection:
            connection.execute(self.database_log_table.insert().values(data))
            connection.commit()

    def read(self, limit: int = 10000) -> t.List[t.Dict[str, t.Any]] | None:
        with self.database_engine.connect() as connection:
            sel = self.database_log_table.select().order_by(
                self.database_log_table.c.traffic_id.desc()
            )
            if limit:
                sel = sel.limit(limit)

            results = connection.execute(sel)

            return [row._asdict() for row in results.fetchall()]
