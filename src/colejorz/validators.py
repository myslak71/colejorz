"""Colejorz validators."""


def validate_post_state_request(body):
    """Validate if state change has correct values."""
    try:
        speed = body['speed']
    except KeyError:
        return {'error': 'Missing "speed" value.'}
    try:
        speed = int(speed)
    except (ValueError, TypeError):
        return {'error': 'Speed value must be a number'}
    if speed > 100 or speed < -100:
        return {'error': 'Speed value must be in range <-100; 100>.'}
    return {}
