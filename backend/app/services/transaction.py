from functools import wraps
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def atomic_mutation(fn):
    """Services own commits; rollback every intermediate write on any failure."""

    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "Conflicto con otra carga. Recargue e intente nuevamente."
            ) from exc
        except Exception:
            self.db.rollback()
            raise

    return wrapped
