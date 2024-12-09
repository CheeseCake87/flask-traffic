import typing as t
from datetime import datetime

if t.TYPE_CHECKING:
    from flask_traffic import Traffic
    from flask_traffic._log_policy import LogPolicy


class StoreProtocol(t.Protocol):
    """
    The protocol to follow for a valid *Store.
    """

    log_policy: "LogPolicy"

    def setup(self, traffic_instance: "Traffic") -> None: ...

    def log(
        self,
        request_date: t.Optional[datetime] = None,
        request_method: t.Optional[str] = None,
        request_endpoint: t.Optional[str] = None,
        request_host_url: t.Optional[str] = None,
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
    ) -> None: ...

    def read(self) -> t.Any: ...
