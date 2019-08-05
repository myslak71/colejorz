"""Colejorz validators."""


def validate_post_state_request(body):
    """Validate if state change has correct values."""
    errors = []
    try:
        speed = int(body['speed'])
    except KeyError:
        errors.append('Missing "speed" value.')
    except (ValueError, TypeError):
        errors.append('Speed value must be a number')

    if not errors and speed > 100 or speed < -100:
        errors.append('Speed value must be in range <-100; 100>.')

    if 'timed' in body:
        if int(body['timed']) < 0:
            errors.append(
                'Timed run value cannot be negative value must be 0 '
                'for not timed run or any positive value.'
            )
    return errors
