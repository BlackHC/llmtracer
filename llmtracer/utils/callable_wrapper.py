#  LLM Tracer
#  Copyright (c) 2023. Andreas Kirsch
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import types
import typing
from dataclasses import dataclass

P = typing.ParamSpec("P")
T = typing.TypeVar("T")


@dataclass
class CallableWrapper:
    """
    A functor that wraps a callable and forwards all attributes to the wrapped callable.
    """

    __wrapped__: object

    def __get__(self, instance: object, owner: type | None = None) -> typing.Callable:
        """Support instance methods."""
        if instance is None:
            return self

        # Bind self to instance as MethodType
        return types.MethodType(self, instance)

    def __getattr__(self, item):
        if item == "__wrapped__":
            raise AttributeError(name=item, obj=self)
        return getattr(self.__wrapped__, item)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __dir__(self) -> typing.Iterable[str]:
        # merge the attributes of the wrapped object with the attributes of the wrapper
        self_dir = list(super().__dir__())
        wrapped_dir = list(dir(self.__wrapped__))
        return list(set(self_dir + wrapped_dir))


# Fix Pydantic (if it is installed) by adding CallableWrapper to UNTOUCHED_TYPES
try:
    import pydantic

    pydantic.main.UNTOUCHED_TYPES += (CallableWrapper,)
except ImportError:
    pass
