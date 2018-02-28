import logging
from functools import wraps

from bluesky.utils import short_uid
from bluesky.plan_stubs import wait as plan_wait, abs_set, checkpoint

def return_to_initial(*devices, perform=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the initial positions of all the inputted devices
            initial_positions = {dev : dev.position for dev in devices}
            try:
                return (yield from func(*args, **kwargs))
            finally:
                # Start returning all the devices to their initial positions
                if perform:
                    yield from checkpoint()
                    group = short_uid('set')
                    for dev, pos in initial_positions.items():
                        yield from abs_set(dev, pos, group=group)
                    # Wait for all the moves to finish if they haven't already
                    yield from plan_wait(group=group)
        return wrapper
    return decorator
