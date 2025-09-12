import typing as t
from datetime import datetime

from .._helpers import prevent_long_paths


from .._globals import IGNORE_LOCALS
from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic
    try:
        from redis import Redis
    except ImportError:
        raise ImportError(
            "You're attempting to use a RedisStore but redis is not installed. "
            "Please install it with `pip install redis`"
        )


class RedisStore:
    client: "Redis"
    log_policy: LogPolicy
    event_name: str

    _traffic_instance = None

    def __repr__(self) -> str:
        return f"<RedisStore client={self.client} log_policy={self.log_policy}>"

    def __init__(
        self,
        redis_host: str,
        event_name: str,
        redis_password: str | None = None,
        redis_port: int = 6379,
        log_policy: LogPolicy | None = None,
    ) -> None:
        try:
            from redis import Redis
        except ImportError:
            raise ImportError(
                "You're attempting to use a RedisStore but redis is not installed. "
                "Please install it with `pip install redis`"
            )
        """
        Create a new RedisStore instance.

        :param redis_host: redis host to connect to
        :param event_name: redis stream name to use for logging traffic data.
        :param redis_password: redis password for authentication
        :param redis_port: redis port on which redis instance is listening on
        :param log_policy: the log policy to use (defaults to log everything if not provided)
        """
        self.client = Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=0,
            decode_responses=True,
        )
        self.event_name = event_name
        if log_policy is None:
            from .._log_policy import LogPolicy

            self.log_policy = LogPolicy()
        else:
            self.log_policy = log_policy

    def setup(self, traffic_instance: "Traffic"):
        """
        Nothing to set up in redis store
        """
        pass

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
        legal_types = (str, int, float, bytes)

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

                if isinstance(locals()[attr], datetime):
                    data[attr] = locals()[attr].isoformat()
                    continue

                if locals()[attr] is None:
                    data[attr] = "None"
                    continue

                if not isinstance(locals()[attr], legal_types):
                    data[attr] = "unknown"
                else:
                    data[attr] = locals()[attr]

            else:
                continue

        self.client.xadd(name=self.event_name, fields=data)

    def read(self) -> t.List[t.Dict[str, t.Any]]:
        """
        Read the Redis stream and return the contents.

        :return: the contents of the redis stream
        """

        logs: t.List[t.Dict[str, t.Any]] = []

        data_stream = self.client.xread(streams={self.event_name: 0})
        if len(data_stream) > 0:
            msg_stream = data_stream[0]
            messages = msg_stream[1]

            for msg in messages:
                logs.append(
                    {
                        key: (None if value == "None" else value)
                        for key, value in msg[1].items()
                    }
                )

        logs.reverse()
        return logs
