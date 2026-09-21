"""Equalize common credential rejection paths; throttling still runs before hashing."""

from functools import wraps
import time
import secrets


def comparable_response(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        start = time.monotonic()
        try:
            return function(*args, **kwargs)
        finally:
            # Covers measured legacy bcrypt + Argon2 migration on this deployment.
            # Not a constant-time guarantee under infrastructure contention.
            remaining = 0.35 + secrets.randbelow(30) / 1000 - (time.monotonic() - start)
            if remaining > 0:
                time.sleep(remaining)

    return wrapped
