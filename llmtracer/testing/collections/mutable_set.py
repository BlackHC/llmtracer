"""See `TestSet` for an example."""
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

from typing import MutableSet, Type

from llmtracer.testing.collections import unordered_equal


class MutableSetTests:
    mutable_set: Type

    @classmethod
    def create_mutable_set(cls) -> MutableSet:
        return cls.mutable_set()

    @staticmethod
    def get_element(i):
        return i

    def test_add_coverage(self):
        instance = self.create_mutable_set()
        element1 = self.get_element(1)

        instance.add(element1)
        # And add a second time for good measure
        instance.add(element1)

    def test_discard_missing_element_passes(self):
        instance = self.create_mutable_set()
        element1 = self.get_element(1)

        instance.discard(element1)

    def test_discard_passes(self):
        instance = self.create_mutable_set()
        element1 = self.get_element(1)

        instance.add(element1)
        instance.discard(element1)

    def test_contains_len(self):
        instance = self.create_mutable_set()
        element1 = self.get_element(1)

        assert len(instance) == 0
        assert element1 not in instance
        instance.add(element1)
        assert element1 in instance
        assert len(instance) == 1

        element2 = self.get_element(2)
        assert element2 not in instance
        instance.add(element2)
        assert element2 in instance
        assert len(instance) == 2

        assert element1 in instance
        instance.discard(element1)
        assert element1 not in instance
        assert len(instance) == 1

        assert element2 in instance
        instance.discard(element2)
        assert element1 not in instance
        assert element2 not in instance
        assert len(instance) == 0

    def test_iter(self):
        instance = self.create_mutable_set()
        element1 = self.get_element(1)
        element2 = self.get_element(2)

        assert list(iter(instance)) == []
        instance.add(element1)
        assert unordered_equal(iter(instance), [element1])

        instance.add(element2)
        assert unordered_equal(iter(instance), [element1, element2])
