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

import enum

from pydantic import BaseModel
from wandb.sdk.data_types import trace_tree

from llmtracer.frame_info import FrameInfo


class TraceNodeKind(str, enum.Enum):
    """
    The type of event.

    We match wandb's span kind for convienence and add more.
    """

    LLM = trace_tree.SpanKind.LLM
    CHAIN = trace_tree.SpanKind.CHAIN
    AGENT = trace_tree.SpanKind.AGENT
    TOOL = trace_tree.SpanKind.TOOL
    SCOPE = "SCOPE"
    CALL = "CALL"
    EVENT = "EVENT"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class TraceNode(BaseModel):
    """
    Node in the trace tree.
    """

    kind: TraceNodeKind
    name: str | None
    event_id: int

    start_time_ms: int
    end_time_ms: int
    running: bool = False

    delta_frame_infos: list[FrameInfo]

    properties: dict[str, object]
    children: list['TraceNode']

    def collect_event_id_map(self, event_id_map=None) -> dict[int, 'TraceNode']:
        """
        Update a map from event id to node.
        """
        if event_id_map is None:
            event_id_map = {}

        event_id_map[self.event_id] = self
        for child in self.children:
            child.collect_event_id_map(event_id_map)
        return event_id_map

    def to_custom_dict(self, include_timing: bool = True, include_lineno: bool = True):
        custom_dict = {
            "kind": self.kind.value,
            "name": self.name,
            "event_id": self.event_id,
            "delta_frame_infos": [
                {
                    "module": frame_info.module,
                    "function": frame_info.function,
                    "code_context": frame_info.code_context,
                }
                | ({"lineno": frame_info.lineno} if include_lineno else {})
                for frame_info in self.delta_frame_infos
            ],
            "properties": self.properties,
            "children": [
                child.to_custom_dict(include_timing=include_timing, include_lineno=include_lineno)
                for child in self.children
            ],
        }
        if include_timing:
            custom_dict["start_time_ms"] = self.start_time_ms
            custom_dict["end_time_ms"] = self.end_time_ms

        return custom_dict


class Trace(BaseModel):
    """
    A trace tree.
    """

    name: str | None
    traces: list[TraceNode]
    properties: dict[str, object]
    unique_objects: dict[str, object]

    def build_event_id_map(self) -> dict[int, TraceNode]:
        """
        Build a map from event id to node.
        """
        event_id_map: dict[int, TraceNode] = {}
        for trace in self.traces:
            trace.collect_event_id_map(event_id_map)
        return event_id_map

    def to_custom_dict(self, include_timing: bool = True, include_lineno: bool = True):
        """
        Convert the trace to a jsonable format.

        Args:
            include_timing: Whether to include timing information.
            include_lineno: Whether to include line number information.

        Returns:
            The jsonable trace.
        """
        return {
            "name": self.name,
            "traces": [
                trace.to_custom_dict(include_timing=include_timing, include_lineno=include_lineno)
                for trace in self.traces
            ],
            "properties": self.properties,
            "unique_objects": self.unique_objects,
        }
