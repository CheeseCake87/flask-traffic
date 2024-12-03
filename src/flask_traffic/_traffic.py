import timeit
import typing as t
from datetime import datetime
from pathlib import Path

from flask import Flask, g, request

from .stores._protocols import StoreProtocol


class Traffic:
    app: Flask
    app_instance_folder: t.Optional[Path]

    stores: t.Union[StoreProtocol, t.List[StoreProtocol]]

    def __init__(
        self,
        app: t.Optional[Flask] = None,
        stores: t.Optional[t.Union[StoreProtocol, t.List[StoreProtocol]]] = None,
    ) -> None:
        if app is not None:
            if stores is None:
                raise ImportError("No stores were passed in.")
            self.init_app(app, stores)

    def init_app(
        self,
        app: Flask,
        stores: t.Union[t.Union[StoreProtocol, t.List[StoreProtocol]]],
    ) -> None:
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

    def _setup_stores(self):
        for store in self.stores:
            store.setup(self)

    def _setup_request_watcher(self):
        @self.app.before_request
        def traffic_before_request():
            g.traffic_timer = timeit.default_timer()

        @self.app.after_request
        def traffic_after_request(response):
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
        def traffic_teardown_request(exception):
            if exception:
                try:
                    message = exception.__repr__()
                except AttributeError:
                    message = str(exception)

                for store in self.stores:
                    if store.log_policy.response_exception:
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
