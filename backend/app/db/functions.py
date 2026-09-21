from sqlalchemy import String
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.ext.compiler import compiles


class normalized_trim(GenericFunction):
    """Explicit PostgreSQL btrim keeps functional-index reflection stable."""

    name = "btrim"
    type = String()
    inherit_cache = True


@compiles(normalized_trim, "sqlite")
def sqlite_trim(element, compiler, **kwargs):
    return "trim(%s)" % compiler.process(element.clauses, **kwargs)
