"""Clearcode Colejorz."""

from pyramid.request import Request
from pyramid.config import Configurator
from wsgiref.simple_server import make_server

from colejorz.stationmaster import StationMaster
from colejorz.views import get_state


def get_stationmaster(request):
    """Return the pilothouse instance."""
    return request.registry.stationmaster


def serve(**settings):
    """Configure and serve the Pyramid WSGI application for colejorz."""
    config = Configurator(settings=settings)
    config.scan('colejorz')
    config.registry.stationmaster = StationMaster()
    config.add_request_method(get_stationmaster, name='stationmaster', property=True, reify=True)
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        config.registry.stationmaster.exit()
        server.server_close()


if __name__ == '__main__':
    serve()
