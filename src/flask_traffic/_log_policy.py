from typing import Optional, Iterable


class LogPolicy:
    """
    The LogPolicy class is used to define what data should be logged
    when a request is made to the Flask app.

    If a LogPolicy is not passed to a store, one is created and all attributes
    are set to True.
    """

    request_date: bool
    request_method: bool
    request_host_url: bool
    request_path: bool
    request_endpoint: bool
    request_remote_address: bool
    request_referrer: bool
    request_user_agent: bool
    request_browser: bool
    request_platform: bool

    response_time: bool
    response_size: bool
    response_status_code: bool
    response_exception: bool
    response_mimetype: bool

    on_endpoints: Iterable
    skip_endpoints: Iterable

    on_status_codes: Iterable
    skip_status_codes: Iterable

    only_on_exception: bool
    skip_on_exception: bool

    max_request_path_length: int

    def __repr__(self) -> str:
        return f"<LogPolicy {self.__dict__}>"

    def __init__(
        self,
        on_endpoints: Optional[Iterable[str]] = None,
        skip_endpoints: Optional[Iterable[str]] = None,
        on_status_codes: Optional[Iterable[str]] = None,
        skip_status_codes: Optional[Iterable[str]] = None,
        only_on_exception: bool = False,
        skip_on_exception: bool = False,
        max_request_path_length: int = 512,
    ) -> None:
        """
        Create a new LogPolicy instance.

        Use either `.set_from_true` or `.set_from_false` methods
        to enable or disable logging of data.

        ::

            log_policy = LogPolicy()
            log_policy.set_from_true(...)
            -or-
            log_policy.set_from_false(...)

        *Default Policy:*

        ::

            request_method = True
            request_host_url = True
            request_path = True
            request_endpoint = True
            request_remote_address = True
            request_referrer = True
            request_user_agent = True
            request_browser = True
            request_platform = True

            response_time = True
            response_size = True
            response_status_code = True
            response_exception = True
            response_mimetype = True

            on_endpoints = None (disabled)
            skip_endpoints = None (disabled)

            on_status_codes = None (disabled)
            skip_status_codes = None (disabled)

            only_on_exception = False
            skip_on_exception = False

            max_request_path_length: int = 512

        :param on_endpoints: only log requests to these endpoints
        :param skip_endpoints: do not log requests to these endpoints
        :param on_status_codes: only log requests with these status codes
        :param skip_status_codes: do not log requests with these status codes
        :param only_on_exception: only create a log entry if an exception is raised during the request if True
        :param skip_on_exception: do not create a log entry if an exception is raised during the request if True
        :param max_request_path_length: the maximum length of the request path to log
        """

        self.request_date = True
        self.request_method = True
        self.request_host_url = True
        self.request_path = True
        self.request_endpoint = True
        self.request_remote_address = True
        self.request_referrer = True
        self.request_user_agent = True
        self.request_browser = True
        self.request_platform = True

        self.response_time = True
        self.response_size = True
        self.response_status_code = True
        self.response_exception = True
        self.response_mimetype = True

        # Endpoints
        if on_endpoints is None:
            self.on_endpoints = set()
        else:
            self.on_endpoints = on_endpoints

        if skip_endpoints is None:
            self.skip_endpoints = set()
        else:
            self.skip_endpoints = skip_endpoints

        # Status Codes
        if on_status_codes is None:
            self.on_status_codes = set()
        else:
            self.on_status_codes = on_status_codes

        if skip_status_codes is None:
            self.skip_status_codes = set()
        else:
            self.skip_status_codes = skip_status_codes

        self.only_on_exception = only_on_exception
        self.skip_on_exception = skip_on_exception

        self.max_request_path_length = max_request_path_length

    def set_from_true(
        self,
        request_date: bool = True,
        request_method: bool = True,
        request_host_url: bool = True,
        request_path: bool = True,
        request_endpoint: bool = True,
        request_remote_address: bool = True,
        request_referrer: bool = True,
        request_user_agent: bool = True,
        request_browser: bool = True,
        request_platform: bool = True,
        response_time: bool = True,
        response_size: bool = True,
        response_status_code: bool = True,
        response_exception: bool = True,
        response_mimetype: bool = True,
    ) -> "LogPolicy":
        """
        Disable what you don't want to log.

        Set the attribute you don't want to log to False.

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
        self.request_date = request_date
        self.request_method = request_method
        self.request_host_url = request_host_url
        self.request_path = request_path
        self.request_endpoint = request_endpoint
        self.request_remote_address = request_remote_address
        self.request_referrer = request_referrer
        self.request_user_agent = request_user_agent
        self.request_browser = request_browser
        self.request_platform = request_platform

        self.response_time = response_time
        self.response_size = response_size
        self.response_status_code = response_status_code
        self.response_exception = response_exception
        self.response_mimetype = response_mimetype

        return self

    def set_from_false(
        self,
        request_date: bool = False,
        request_method: bool = False,
        request_host_url: bool = False,
        request_path: bool = False,
        request_endpoint: bool = False,
        request_remote_address: bool = False,
        request_referrer: bool = False,
        request_user_agent: bool = False,
        request_browser: bool = False,
        request_platform: bool = False,
        response_time: bool = False,
        response_size: bool = False,
        response_status_code: bool = False,
        response_exception: bool = False,
        response_mimetype: bool = False,
    ) -> "LogPolicy":
        """
        Enable what you want to log.

        Set the attribute you want to log to True.

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
        self.request_date = request_date
        self.request_method = request_method
        self.request_host_url = request_host_url
        self.request_path = request_path
        self.request_endpoint = request_endpoint
        self.request_remote_address = request_remote_address
        self.request_referrer = request_referrer
        self.request_user_agent = request_user_agent
        self.request_browser = request_browser
        self.request_platform = request_platform

        self.response_time = response_time
        self.response_size = response_size
        self.response_status_code = response_status_code
        self.response_exception = response_exception
        self.response_mimetype = response_mimetype

        return self
