"""See `TestDict` for an example."""
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

from typing import MutableMapping, Type

import pytest

from llmtracer.testing.collections import unordered_equal


class MutableMappingTests:
    mutable_mapping: Type

    @classmethod
    def create_mutable_mapping(cls) -> MutableMapping:
        return cls.mutable_mapping()

    @staticmethod
    def get_key(i):
        return i

    @staticmethod
    def get_value(i):
        return str(i)

    def get_key_value(self, i):
        return self.get_key(i), self.get_value(i)

    def test_get_missing_fails(self):
        instance = self.create_mutable_mapping()
        with pytest.raises(KeyError):
            # noinspection PyStatementEffect
            instance[self.get_key(1)]

    def test_del_missing_fails(self):
        instance = self.create_mutable_mapping()
        with pytest.raises(KeyError):
            del instance[self.get_key(1)]

    def test_integration(self):
        instance = self.create_mutable_mapping()

        assert len(instance) == 0
        assert list(iter(instance)) == []

        key, value = self.get_key_value(1)
        instance[key] = value

        assert instance[key] == value
        assert unordered_equal(list(iter(instance)), [key])
        assert len(instance) == 1

        key2, value2 = self.get_key_value(2)
        instance[key2] = value2

        assert instance[key2] == value2
        assert unordered_equal(list(iter(instance)), [key, key2])
        assert len(instance) == 2

        value3 = self.get_value(3)
        instance[key] = value3
        assert instance[key] == value3

        del instance[key]
        assert key not in instance
        assert unordered_equal(list(iter(instance)), [key2])
        assert len(instance) == 1
