import weakref
from typing import Dict, Generic, Iterator, MutableMapping, MutableSet, TypeVar

KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.
KT_co = TypeVar('KT_co', covariant=True)  # Value type covariant containers.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.


def supports_weakrefs(value):
    """Determine if the given value supports weak references."""
    return type(value).__weakrefoffset__ != 0


# import objproxies
# class ObjectProxy(objproxies.ObjectProxy):
#     __slots__ = ("__weakref__",)


class IdMapFinalizer(Generic[KT]):
    id_to_finalizer: Dict[int, weakref.finalize]

    def __init__(self):
        self.id_to_finalizer = {}

    def _finalizer(self, id_value, custom_handler):
        del self.id_to_finalizer[id_value]
        if custom_handler is not None:
            custom_handler(id_value)

    def __contains__(self, item):
        return id(item) in self.id_to_finalizer

    def __len__(self):
        return len(self.id_to_finalizer)

    def __iter__(self):
        # TODO: add a test that shows that this is necessary to avoid deletions
        # Take a snapshot of the keys. This will ensure that the dictionary will be stable during iteration.
        return iter(list(map(self.get_object, self.id_to_finalizer)))

    def get_object(self, id_value):
        return self.id_to_finalizer[id_value].peek()[0]

    def register(self, value: KT, custom_handler):
        if not supports_weakrefs(value):
            # TODO: log?
            return

        id_value = id(value)
        if id_value in self.id_to_finalizer:
            raise ValueError(f"{value} has already been added to the finalizer!")

        self.id_to_finalizer[id_value] = weakref.finalize(value, self._finalizer, id_value, custom_handler)

    def release(self, value: KT):
        id_value = id(value)
        finalizer = self.id_to_finalizer.get(id_value)
        if finalizer is not None:
            finalizer.detach()
            del self.id_to_finalizer[id_value]

    def clear(self):
        for finalizer in self.id_to_finalizer.values():
            finalizer.detach()
        self.id_to_finalizer.clear()

    def __del__(self):
        self.clear()


# TODO: add tests
class WeakIdSet(MutableSet[T]):
    id_map_finalizer: IdMapFinalizer

    def __init__(self):
        self.id_map_finalizer = IdMapFinalizer()

    def add(self, x: T) -> None:
        assert supports_weakrefs(x)
        if x not in self.id_map_finalizer:
            self.id_map_finalizer.register(x, None)

    def discard(self, x: T) -> None:
        self.id_map_finalizer.release(x)

    def __contains__(self, x: object) -> bool:
        return x in self.id_map_finalizer

    def __len__(self) -> int:
        return len(self.id_map_finalizer)

    def __iter__(self) -> Iterator[T]:
        return iter(self.id_map_finalizer)

    def __repr__(self):
        return f"WeakIdSet{{{ ', '.join(map(repr, self))}}}"


class WeakKeyIdMap(MutableMapping[KT, VT]):
    id_map_to_value: Dict[int, VT]
    id_map_finalizer: IdMapFinalizer

    def __init__(self):
        self.id_map_to_value = {}
        self.id_map_finalizer = IdMapFinalizer()

    def _release(self, id_value):
        del self.id_map_to_value[id_value]

    def __setitem__(self, k: KT, v: VT) -> None:
        assert supports_weakrefs(k)

        id_k = id(k)
        if id_k not in self.id_map_to_value:
            self.id_map_finalizer.register(k, self._release)
        self.id_map_to_value[id_k] = v

    def __delitem__(self, k: KT) -> None:
        del self.id_map_to_value[id(k)]
        self.id_map_finalizer.release(k)

    def __getitem__(self, k: KT) -> VT:
        return self.id_map_to_value[id(k)]

    def __len__(self) -> int:
        return len(self.id_map_to_value)

    def __iter__(self) -> Iterator[KT]:
        # TODO: add a test that shows that this is necessary to avoid deletions
        # Take a snapshot of the keys. This will ensure that the dictionary will be stable during iteration.
        return iter(self.id_map_finalizer)

    def __repr__(self):
        return f"KeyIdDict{{{', '.join(map(lambda key: f'{repr(key)}:{repr(self[key])}', self))}}}"


class AbstractWrappedValueMutableMapping(Generic[KT, VT, T], MutableMapping[KT, VT]):
    data: Dict[KT, T]

    def __init__(self):
        self.data = {}

    def value_to_store(self, v: VT) -> T:
        raise NotImplementedError()

    def store_to_value(self, v: T) -> VT:
        raise NotImplementedError()

    def __setitem__(self, k: KT, v: VT) -> None:
        self.data[k] = self.value_to_store(v)

    def __delitem__(self, v: KT) -> None:
        del self.data[v]

    def __getitem__(self, k: KT) -> VT:
        return self.store_to_value(self.data[k])

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[KT]:
        return iter(self.data)
