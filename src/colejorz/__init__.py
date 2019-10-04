"""Clearcode Colejorz."""
from collections import OrderedDict
from typing import Callable, Dict, Any
from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router

from colejorz.stationmaster import StationMaster
from colejorz.views import get_state


def get_stationmaster(request: Request) -> StationMaster:
    """Return the pilothouse instance."""
    return request.registry.stationmaster


def app_factory(
        global_config: OrderedDict,  # pylint:disable=unused-argument
        **settings: Any
):
    """Configure and serve the Pyramid WSGI application for colejorz."""
    with Configurator(settings=settings) as config:
        config.scan('colejorz')
        config.registry.stationmaster = StationMaster()
        config.add_request_method(
            get_stationmaster,
            name='stationmaster',
            property=True,
            reify=True
        )
        app = config.make_wsgi_app()
        return app


def server_factory(
        global_config: OrderedDict,  # pylint:disable=unused-argument
        host: str,
        port: str
) -> Callable[[Router], None]:
    """Return WSGI serving function reference."""
    app_port = int(port)

    def serve(app: Router) -> None:
        """Serve the application."""
        server = make_server(host, app_port, app)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            # close the pilothouse
            app.registry.stationmaster.exit()
            server.server_close()

    return serve
