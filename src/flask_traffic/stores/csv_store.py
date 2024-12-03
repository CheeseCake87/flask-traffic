import csv
import typing as t
from datetime import datetime
from pathlib import Path

from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic


class CSVStore:
    filename: str
    location: t.Optional[t.Union[str, Path]]

    filepath: Path
    log_policy: LogPolicy

    _traffic_instance = None

    def __init__(
        self,
        filename: str = "traffic.csv",
        location: t.Optional[t.Union[str, Path]] = None,
        log_policy: LogPolicy = None,
    ) -> None:
        self.filename = filename
        self.location = location

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

    def setup(self, traffic_instance: "Traffic") -> None:
        # set filepath to instance folder if location is None
        if self.location is None:
            self.filepath = traffic_instance.app_instance_folder / self.filename
        else:
            # This expects an absolute path
            if isinstance(self.location, str):
                self.filepath = Path(self.location) / self.filename

            # This expects a Path object
            if isinstance(self.location, Path):
                self.filepath = self.location / self.filename

        # create the file if it doesn't exist
        if not self.filepath.exists():
            # create the parent directory if it doesn't exist
            if not self.filepath.parent.exists():
                self.filepath.parent.mkdir(parents=True)

            # file is created here
            self.filepath.touch()

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

        with open(self.filepath, "a+") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())  # type: ignore

            if f.tell() == 0:
                # write the header if the file is empty
                writer.writeheader()

            writer.writerow(data)
