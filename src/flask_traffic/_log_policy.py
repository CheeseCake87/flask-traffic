class LogPolicy:
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
    ):
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
