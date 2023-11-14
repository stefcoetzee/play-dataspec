"""Dataspec validation functions"""

from typing import Iterator
from functools import wraps

from dataspec import s, ErrorDetails, ValidationError, ValidatorFn


def make_vfn(spec) -> ValidatorFn:
    """Return validator function for provided `spec`."""

    def vfn(v) -> Iterator[ErrorDetails]:
        if not spec.is_valid(v):
            yield next(spec.validate(v))

    return vfn


def validate_one(spec):
    """
    Decorator that accepts a `spec` to validate one value or collection against
    (i.e. the argument of the decorated function).
    Multiple decorated function arguments are not allowed.
    """

    def add_validation(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if len(args) + len(kwargs) != 1:
                raise TypeError("Only one argument or keyword allowed.")

            vspec = s(make_vfn(spec))

            try:
                if args:
                    vspec.validate_ex(*args)
                else:
                    vspec.validate_ex(*kwargs.values())

                return fn(*args, **kwargs)

            except ValidationError as e:
                raise e

        return wrapper

    return add_validation


def validate_data(spec, data):
    """
    Validate `data` against `spec`.
    Raises exception for invalid data, returns `True` otherwise
    """
    vspec = s(make_vfn(spec))

    try:
        vspec.validate_ex(data)
        return True
    except ValidationError as e:
        raise e
