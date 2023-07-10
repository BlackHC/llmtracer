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

import gc
from dataclasses import dataclass

import pytest

from llmtracer.testing.collections.mutable_mapping import MutableMappingTests
from llmtracer.testing.collections.mutable_set import MutableSetTests
from llmtracer.utils import weakrefs


class DummySupportsWeakRefs:
    pass


class DummyDoesNotSupportWeakRefs:
    __slots__ = ()


@dataclass
class DummyDataclass:
    field: str


def test_supports_weakref():
    assert not weakrefs.supports_weakrefs(1)
    # This is slightly surprising to be honest...
    assert not weakrefs.supports_weakrefs(object())

    assert weakrefs.supports_weakrefs(DummySupportsWeakRefs())
    assert not weakrefs.supports_weakrefs(DummyDoesNotSupportWeakRefs())

    assert weakrefs.supports_weakrefs(DummyDataclass("Hello"))


def test_id_map_finalizer():
    id_map_finalizer = weakrefs.IdMapFinalizer()

    a = DummySupportsWeakRefs()

    a_has_been_finalized_counter = 0
    id_a = id(a)

    def custom_handler(id_value):
        nonlocal a_has_been_finalized_counter
        assert id_value == id_a
        a_has_been_finalized_counter += 1

    id_map_finalizer.register(a, custom_handler)

    with pytest.raises(ValueError):
        id_map_finalizer.register(a, None)

    # Don't throw and don't do anything when we add a value that can't be weakref'ed.
    id_map_finalizer.register(1, None)

    assert set(id_map_finalizer) == {a}

    id_map_finalizer.release(a)

    assert a_has_been_finalized_counter == 0

    id_map_finalizer.register(a, custom_handler)
    gc.collect()

    assert id_map_finalizer.get_object(id(a)) == a

    assert a_has_been_finalized_counter == 0

    a = None
    gc.collect()

    assert a_has_been_finalized_counter == 1


def test_weak_key_id_map():
    weak_key_id_map = weakrefs.WeakKeyIdMap()

    a = DummySupportsWeakRefs()
    b = DummySupportsWeakRefs()

    weak_key_id_map[a] = 1
    weak_key_id_map[b] = 2

    gc.collect()

    assert a in weak_key_id_map
    assert b in weak_key_id_map

    assert weak_key_id_map[a] == 1
    assert weak_key_id_map[b] == 2

    a = None
    gc.collect()

    assert a not in weak_key_id_map
    assert weak_key_id_map == {b: 2}

    b = None
    gc.collect()

    assert not weak_key_id_map


@dataclass
class BoxedValue:
    i: int


class TestWeakKeyIdMap(MutableMappingTests):
    mutable_mapping = weakrefs.WeakKeyIdMap

    @staticmethod
    def get_key(i):
        return BoxedValue(i)


class TestWrappedValueMutableMapping(MutableMappingTests):
    class WrappedValueMutableMappingInstance(weakrefs.AbstractWrappedValueMutableMapping):
        @staticmethod
        def value_to_store(v):
            return (v,)

        @staticmethod
        def store_to_value(v):
            return v[0]

    @staticmethod
    def create_mutable_mapping():
        return TestWrappedValueMutableMapping.WrappedValueMutableMappingInstance()


class TestWeakIdSet(MutableSetTests):
    mutable_set = weakrefs.WeakIdSet

    @staticmethod
    def get_element(i):
        return BoxedValue(i)
