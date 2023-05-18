import dataclasses
import inspect
import typing
from dataclasses import dataclass, field
from functools import partial

import pydantic

T = typing.TypeVar("T")

ObjectConverter: typing.TypeAlias = typing.Callable[[typing.Any, typing.Optional['ObjectConverter']], typing.Any]


@typing.no_type_check
def simple_object_converter(obj: typing.Any, preferred_converter: ObjectConverter | None = None) -> typing.Any:
    if preferred_converter is None:
        preferred_converter = simple_object_converter

    if isinstance(obj, pydantic.BaseModel):
        return convert_pydantic_model(obj, preferred_converter)
    elif not isinstance(obj, type) and dataclasses.is_dataclass(obj):
        return {preferred_converter(f.name): preferred_converter(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, tuple):
        return tuple(preferred_converter(v) for v in obj)
    elif isinstance(obj, list):
        return [preferred_converter(v) for v in obj]
    elif isinstance(obj, set):
        return {preferred_converter(v) for v in obj}
    elif isinstance(obj, dict):
        return {preferred_converter(k): preferred_converter(v) for k, v in obj.items()}

    return repr(obj)


@dataclass
class DynamicObjectConverter:
    """
    A class that converts objects to JSON dicts or strings.
    By default, only literals, tuples, lists, sets, dicts and dataclasses are converted.
    Other objects are {}.

    Additional classes can be added with the `add_converter` decorator.
    """

    default_converter: ObjectConverter = simple_object_converter
    converters: dict[type, typing.Callable[[typing.Any, ObjectConverter], typing.Any] | None] = field(
        default_factory=dict
    )

    def __call__(self, obj: object, preferred_converter: ObjectConverter | None = None):
        if preferred_converter is None:
            preferred_converter = self

        for t in reversed(self.converters):
            if not isinstance(obj, t):
                continue

            converter = self.converters[t]
            if converter is not None:
                return converter(obj, preferred_converter)
            else:
                return f'{obj.__class__.__module__}:{obj.__class__.__qualname__} @ {hex(id(obj))}'

        return self.default_converter(obj, preferred_converter)  # type: ignore

    def register_converter(
        self, func: typing.Callable[[T, ObjectConverter], dict] | None = None, type_: type[T] | None = None
    ):
        """
        Registers a converter for a type.

        This can be called as a decorator or as a function.
        """
        if func is None:
            # return a decorator that adds a converter for type_
            return partial(self.register_converter, type_=type_)

        if type_ is None:
            # get the type from the function annotation (the first argument to func)
            signature = inspect.signature(func)
            type_ = list(signature.parameters.values())[0].annotation

            # fail is there no annotation
            if type_ is inspect.Parameter.empty:
                raise ValueError(
                    "No type annotation for the first argument to the converter function. Please pass the "
                    "type as the type_ argument to register_converter or add a type annotation."
                )

            # check if type_ is Annoated
            if hasattr(type_, '__metadata__'):
                assert hasattr(type_, '__origin__')
                # get the actual type
                type_ = type_.__origin__  # type: ignore

            assert type_ is not None, "type_ is None"

        self.converters[type_] = func

        return func

    def add_converter(self, func: typing.Callable[[T, ObjectConverter], dict] | None = None):
        """
        Decorator that adds a converter to the ObjectConverter class that is wrapped.
        """

        def wrapper(type_: type):
            if func is None:
                # Check if type_ is a Pydantic model
                if isinstance(type_, type) and issubclass(type_, pydantic.BaseModel):
                    # Add a converter for the model
                    self.register_converter(convert_pydantic_model, type_)
                else:
                    raise ValueError("add_converter can only be used with Pydantic models.")

            # Add a converter for the type
            self.register_converter(func, type_)

            return type_

        return wrapper


def convert_pydantic_model(obj: pydantic.BaseModel, converter: ObjectConverter | None = None) -> dict:
    """
    Converts a pydantic model to a dict.
    """
    if converter is None:
        converter = convert_pydantic_model

    # Iterate over the fields of the model
    return {f.name: converter(getattr(obj, f.name)) for f in obj.__fields__.values()}  # type: ignore
