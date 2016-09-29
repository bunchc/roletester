import time

# Interval in seconds
_LAST_RUN = 0
_INTERVAL = 5
_BETWEEN = 5

def throttled(some_function):
    def wrapper(*args, **kwargs):
        global _LAST_RUN
        while time.time() - _LAST_RUN < _BETWEEN:
            time.sleep(_INTERVAL)
        result = some_function(*args, **kwargs)
        _LAST_RUN = time.time()
        return result
    return wrapper
