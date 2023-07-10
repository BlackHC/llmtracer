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

from llmtracer import build_trace, event_scope, trace_calls


def test_trace():
    with build_trace(module_filters=__name__, stack_frame_context=0).scope() as builder:
        with event_scope("foo"):
            with event_scope("bar"):
                with event_scope("baz"):
                    pass

    assert builder is not None
    assert builder.build().to_custom_dict(include_timing=False, include_lineno=False)['traces'] == [
        {
            'children': [
                {
                    'children': [
                        {
                            'children': [
                                {
                                    'children': [],
                                    'delta_frame_infos': [],
                                    'event_id': 4,
                                    'kind': 'SCOPE',
                                    'name': 'baz',
                                    'properties': {},
                                }
                            ],
                            'delta_frame_infos': [],
                            'event_id': 3,
                            'kind': 'SCOPE',
                            'name': 'bar',
                            'properties': {},
                        }
                    ],
                    'delta_frame_infos': [],
                    'event_id': 2,
                    'kind': 'SCOPE',
                    'name': 'foo',
                    'properties': {},
                }
            ],
            'delta_frame_infos': [],
            'event_id': 1,
            'kind': 'SCOPE',
            'name': None,
            'properties': {},
        }
    ]


def test_trace_calls():
    @trace_calls(capture_args=True, capture_return=True)
    def f(value: int):
        return value * 3

    with build_trace(
        module_filters=__name__,
        stack_frame_context=0,
    ).scope() as builder:
        f(3)
        f(5)

    assert builder is not None
    traces = builder.build().to_custom_dict(include_timing=False, include_lineno=False)['traces']
    assert traces == [
        {
            'children': [
                {
                    'children': [],
                    'delta_frame_infos': [],
                    'event_id': 2,
                    'kind': 'CALL',
                    'name': 'f',
                    'properties': {'arguments': {'value': 3}, 'result': 9},
                },
                {
                    'children': [],
                    'delta_frame_infos': [],
                    'event_id': 3,
                    'kind': 'CALL',
                    'name': 'f',
                    'properties': {'arguments': {'value': 5}, 'result': 15},
                },
            ],
            'delta_frame_infos': [],
            'event_id': 1,
            'kind': 'SCOPE',
            'name': None,
            'properties': {},
        }
    ]
