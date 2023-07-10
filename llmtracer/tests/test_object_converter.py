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

from dataclasses import dataclass

import pydantic

from llmtracer.object_converter import DynamicObjectConverter, ObjectConverter


def test_object_converter():
    # create an ObjectConverter
    converter = DynamicObjectConverter()

    # add a converter for a dataclass
    @dataclass
    class Test:
        a: int
        b: str

    # Check that a vanilla dataclass is converted automatically
    assert converter(Test(1, '2')) == {'a': 1, 'b': '2'}

    def convert_test(test: Test, converter: ObjectConverter):
        return {'a': test.a + 1, 'b': test.b}

    converter.register_converter(convert_test, Test)

    # Check that the converter is used
    assert converter(Test(1, '2')) == {'a': 1 + 1, 'b': '2'}

    # add a converter for a Pydantic model
    @converter.add_converter()
    class TestModel(pydantic.BaseModel):
        a: int
        b: str

    # convert a Pydantic model
    assert converter(TestModel(a=1, b='2')) == {'a': 1, 'b': '2'}

    # convert a dict
    assert converter({'a': 1, 'b': '2'}) == {'a': 1, 'b': '2'}

    # convert an object that is not a dict, dataclass, or Pydantic model
    assert converter(TestModel) == repr(TestModel)

    # convert a list
    assert converter([1, 2, 3]) == [1, 2, 3]

    # convert a set
    assert converter({1, 2, 3}) == {1, 2, 3}

    # convert a tuple
    assert converter((1, 2, 3)) == (1, 2, 3)

    # convert a string
    assert converter('test') == 'test'

    # convert an int
    assert converter(1) == 1

    # convert a nested object
    assert converter({'a': Test(1, '2')}) == {'a': {'a': 2, 'b': '2'}}
