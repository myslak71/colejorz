"""Colejorz REST API views."""
from pyramid.view import view_config

from colejorz.validators import validate_post_state_request


@view_config(name='state', renderer='json', request_method='GET')
def get_state(request):
    """
    GET info about a state of a train.

    Returns JSON response with the train status.
    {'speed': <-100; 100>}, where the number is a percentage of a maximal
    speed. Negative numbers mean going backward, positive numbers mean going
    forward.
    """
    return request.stationmaster.state


@view_config(name='state', renderer='json', request_method='POST')
def set_state(request):
    """
    POST to change the train state.

    Request must contain {'speed': <-100; 100>} to be valid.
    Request might contain timed field for timed runs
    {'speed': <-100; 100>, 'timed': <0; Inf>}
    Where the number is a percentage of a maximal speed.
    Negative numbers mean going backward, positive numbers mean going forward.
    Returns JSON response with the train status.
    """
    body = request.json_body
    errors = validate_post_state_request(body)
    if errors:
        request.response.status_int = 400
        return {'errors': errors}
    request.stationmaster.change_state(
        int(body['speed']),
        int(body.get('timed', 0))
    )
    return {'body': body, 'state': request.stationmaster.state}


@view_config(name='status', renderer='json', request_method='GET')
def get_status(request):
    """Return train status."""
    return {'status': request.stationmaster.train_status}
