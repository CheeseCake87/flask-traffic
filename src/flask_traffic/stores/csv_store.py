import csv
import typing as t
from datetime import datetime
from pathlib import Path

from .._globals import IGNORE_LOCALS
from .._log_policy import LogPolicy

if t.TYPE_CHECKING:
    from .._traffic import Traffic


class CSVStore:
    filename: str
    location: t.Optional[t.Union[str, Path]]

    filepath: Path
    log_policy: LogPolicy

    _traffic_instance = None

    def __repr__(self) -> str:
        return f"<CSVStore filename={self.filepath} log_policy={self.log_policy}>"

    def __init__(
        self,
        filename: str = "traffic.csv",
        location: t.Optional[t.Union[str, Path]] = None,
        log_policy: LogPolicy = None,
    ) -> None:
        """
        Create a new CSVStore instance.

        :param filename: the name of the CSV file to store the traffic data in
        :param location: the location of the CSV file
        :param log_policy: the log policy to use (defaults to log everything if not provided)
        """
        self.filename = filename
        self.location = location

        if log_policy is None:
            from .._log_policy import LogPolicy

            self.log_policy = LogPolicy()

        else:
            self.log_policy = log_policy

    def setup(self, traffic_instance: "Traffic") -> None:
        """
        Set up the CSVStore instance.

        :param traffic_instance:
        :return:
        """
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

    def read(self) -> t.List[t.Dict[str, t.Any]]:
        """
        Read the CSV file and return the data as a list of dictionaries.

        :return: the data as a list of dictionaries
        """
        with open(self.filepath, "r") as f:
            reader = csv.DictReader(f)

            return list(reversed(list(reader)))
