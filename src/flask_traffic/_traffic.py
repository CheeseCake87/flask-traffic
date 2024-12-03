import timeit
import typing as t
from datetime import datetime
from pathlib import Path

from flask import Flask, g, request
from flask import Response

from .stores._protocols import StoreProtocol


class Traffic:
    """
    The Traffic class registers the extension with the Flask app and
    sets up any passed in stores.
    """
    app: Flask
    app_instance_folder: t.Optional[Path]

    stores: t.Union[StoreProtocol, t.List[StoreProtocol]]

    def __init__(
        self,
        app: t.Optional[Flask] = None,
        stores: t.Optional[t.Union[StoreProtocol, t.List[StoreProtocol]]] = None,
    ) -> None:
        """
        Initialize the flask-traffic extension.

        :param app: the flask app to attach the extension to
        :param stores: a single store or stores to log traffic data to
        """
        if app is not None:
            if stores is None:
                raise ImportError("No stores were passed in.")
            self.init_app(app, stores)

    def init_app(
        self,
        app: Flask,
        stores: t.Union[t.Union[StoreProtocol, t.List[StoreProtocol]]],
    ) -> None:
        """
        Initialize the flask-traffic extension.

        :param app: the flask app to attach the extension to
        :param stores: a single store or stores to log traffic data to
        """
        if app is None:
            raise ImportError(
                "No app was passed in, do traffic = Traffic(flaskapp) or traffic.init_app(app)"
            )
        if not isinstance(app, Flask):
            raise TypeError("The app that was passed in is not an instance of Flask")

        self.app = app
        self.app.extensions["traffic"] = self
        self.app_instance_folder = Path(app.instance_path)

        if isinstance(stores, list):
            self.stores = stores
        else:
            self.stores = [stores]

        self._setup_stores()
        self._setup_request_watcher()

    def _setup_stores(self) -> None:
        """
        Private method.
        Set up the stores that were passed in.
        :return:
        """
        for store in self.stores:
            store.setup(self)

    def _setup_request_watcher(self) -> None:
        """
        Private method.
        Set up before, after and teardown functions.
        :return:
        """

        @self.app.before_request
        def traffic_before_request():
            g.traffic_timer = timeit.default_timer()

        @self.app.after_request
        def traffic_after_request(response) -> Response:
            for store in self.stores:
                if not store.log_policy.log_only_on_exception:
                    store.log(
                        request_date=datetime.now(),
                        request_method=request.method,
                        request_path=request.path,
                        request_user_agent=request.user_agent.string,
                        request_remote_address=request.remote_addr,
                        request_referrer=request.referrer,
                        request_browser=request.user_agent.browser,
                        request_platform=request.user_agent.platform,
                        response_time=int(
                            (timeit.default_timer() - g.traffic_timer) * 1000
                        ),
                        response_size=response.content_length,
                        response_status_code=response.status_code,
                        response_exception=None,
                        response_mimetype=response.mimetype,
                    )

            return response

        @self.app.teardown_request
        def traffic_teardown_request(exception: t.Any) -> None:
            if exception:
                try:
                    message = exception.__repr__()
                except AttributeError:
                    message = str(exception)

                for store in self.stores:
                    if not store.log_policy.skip_log_on_exception:
                        store.log(
                            request_date=datetime.now(),
                            request_method=request.method,
                            request_path=request.path,
                            request_user_agent=request.user_agent.string,
                            request_remote_address=request.remote_addr,
                            request_referrer=request.referrer,
                            request_browser=request.user_agent.browser,
                            request_platform=request.user_agent.platform,
                            response_time=int(
                                (timeit.default_timer() - g.traffic_timer) * 1000
                            ),
                            response_size=None,
                            response_status_code=500,
                            response_exception=message,
                            response_mimetype=None,
                        )
