class LogPolicy:
    """
    The LogPolicy class is used to define what data should be logged
    when a request is made to the Flask app.

    Every attribute defaults to False, so that you can enable only the
    data you want to log.

    If a LogPolicy is not passed to a store, one is created and all attributes
    are set to True.
    """
    request_date: bool
    request_method: bool
    request_path: bool
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

    log_only_on_exception: bool = False

    def __init__(
        self,
        request_date: bool = False,
        request_method: bool = False,
        request_path: bool = False,
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
        log_only_on_exception: bool = False,
    ) -> None:
        """
        Create a new LogPolicy instance.

        :param request_date: store the request date if True
        :param request_method: store the request method if True
        :param request_path: store the request path if True
        :param request_remote_address: store the request remote address if True
        :param request_referrer: store the request referrer if True
        :param request_user_agent: store the request user agent if True
        :param request_browser: store the request browser if True
        :param request_platform: store the request platform if True
        :param response_time: store the response time if True
        :param response_size: store the response size if True
        :param response_status_code: store the response status code if True
        :param response_exception: store the response exception if True
        :param response_mimetype: store the response mimetype if True
        :param log_only_on_exception: only create a log entry if an exception is raised during the request if True
        """
        self.request_date = request_date
        self.request_method = request_method
        self.request_path = request_path
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

        self.log_only_on_exception = log_only_on_exception
