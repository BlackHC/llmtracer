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

import json
import pprint  # noqa: F401
import threading
import typing
import weakref
from enum import Enum

import reflex as rx
import reflex.pc as cli
from pydantic import Field
from starlette import status

from llmtracer import Trace, TraceNode, TraceNodeKind

from .flame_graph import FlameGraphNode, flame_graph
from .json_view import json_view
from .pcconfig import config

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


# solarized colors as HTML hex
# https://ethanschoonover.com/solarized/
class SolarizedColors(str, Enum):
    base03 = "#002b36"
    base02 = "#073642"
    base01 = "#586e75"
    base00 = "#657b83"
    base0 = "#839496"
    base1 = "#93a1a1"
    base2 = "#eee8d5"
    base3 = "#fdf6e3"
    yellow = "#b58900"
    orange = "#cb4b16"
    red = "#dc322f"
    magenta = "#d33682"
    violet = "#6c71c4"
    blue = "#268bd2"
    cyan = "#2aa198"
    green = "#859900"


class NodeInfo(rx.Base):
    node_name: str
    kind: TraceNodeKind
    event_id: int
    start_time_ms: int
    end_time_ms: int
    # delta_frame_infos: list[dict[str, object]]
    properties: object | None
    exception: object | None
    self_object: object | None
    result: object | None
    arguments: object | None


class Wrapper(rx.Base):
    inner: object = None

    def __init__(self, inner):
        super().__init__(inner=inner)


def load_example_trace():
    return Trace.parse_file('optimization_unit_trace_example.json')


async def send_event(state: rx.State, event_handler: rx.event.EventHandler):
    """Send an event to the server (from a different client thread)."""
    events = rx.event.fix_events([event_handler], state.get_token())
    state_update = rx.state.StateUpdate(delta={}, events=events)
    state_update_json = state_update.json()

    await app.sio.emit(str(rx.constants.SocketEvent.EVENT), state_update_json, to=state.get_sid(), namespace="/event")


class StreamedTracesSingleton:
    """A class that streams a trace to the client."""

    traces: dict[str, Trace] = {}
    _receivers: weakref.WeakValueDictionary[str, rx.State] = weakref.WeakValueDictionary()

    lock: threading.Lock = threading.Lock()

    def send_update_event(self, origin: rx.State | None, trace_name: str):
        """Send an update event to all registered states (except the one that triggered the update)."""
        if origin is not None:
            origin = origin.parent_state if origin.parent_state else origin

        async def send_events():
            # send an event
            for state in self._receivers.values():
                if origin is None or state.get_sid() != origin.get_sid():
                    # noinspection PyNoneFunctionAssignment,PyArgumentList
                    event_handler: rx.event.EventHandler = State.on_injected_trace(trace_name)  # type: ignore
                    print(f"Sending update event for trace {trace_name} to {state.get_sid()}")
                    await send_event(state, event_handler)

        print(f"Sending update event for trace {trace_name}")
        app.sio.start_background_task(send_events)

    def update_trace(self, trace_name: str, trace: Trace):
        """Update the trace with the given name."""
        with self.lock:
            print(f"Updating trace {trace_name}")
            self.traces[trace_name] = trace
            self.send_update_event(None, trace_name)

    def register_state(self, state: rx.State):
        """Register a state to receive update events.

        We use this to keep track of active clients using a weakref value dictionary.
        """
        main_state: rx.State = state.parent_state if state.parent_state else state
        # TODO: check that we have exactly one state per session id?
        if main_state.get_sid() not in self._receivers:
            self._receivers[main_state.get_sid()] = main_state


def convert_trace_node_kind_to_color(kind: TraceNodeKind):
    if kind == TraceNodeKind.SCOPE:
        return SolarizedColors.base1
    elif kind == TraceNodeKind.AGENT:
        return SolarizedColors.green
    elif kind == TraceNodeKind.LLM:
        return SolarizedColors.blue
    elif kind == TraceNodeKind.CHAIN:
        return SolarizedColors.cyan
    elif kind == TraceNodeKind.CALL:
        return SolarizedColors.yellow
    elif kind == TraceNodeKind.EVENT:
        return SolarizedColors.orange
    elif kind == TraceNodeKind.TOOL:
        return SolarizedColors.magenta
    else:
        return SolarizedColors.base2


def convert_node_to_color(node: TraceNode):
    if "exception" in node.properties:
        return SolarizedColors.red
    else:
        return "black"


def convert_trace_to_flame_graph_data(trace: Trace) -> dict:
    def convert_node(node: TraceNode, discount=1.0) -> FlameGraphNode:
        children = []
        last_ms = node.start_time_ms
        for child in node.children:
            gap_s = child.start_time_ms - last_ms
            if gap_s > 0:
                children.append(
                    FlameGraphNode(
                        name="",
                        background_color="#00000000",
                        value=gap_s,
                        children=[],
                    )
                )
            children.append(convert_node(child, discount=discount * 0.95))
            last_ms = child.end_time_ms

        duration_s = node.end_time_ms - node.start_time_ms
        node_name = node.name or "/Unnamed/"
        return FlameGraphNode(
            id=str(node.event_id),
            name=node_name if not node.running else f"{node_name} (*)",
            value=duration_s * discount,
            children=children,
            background_color=convert_trace_node_kind_to_color(node.kind),
            color=convert_node_to_color(node),
        )

    converted_node = convert_node(trace.traces[-1]).dict(exclude_unset=True)
    return converted_node


class State(rx.State):
    """The app state."""

    __slots__ = [
        '__weakref__',
        'flame_graph_data',
        'current_node',
        'trace_name',
        'injected_trace_names',
    ]

    flame_graph_data: dict = FlameGraphNode(name="", value=1, background_color="#00000000", children=[]).dict()
    current_node: list[NodeInfo] = Field(default_factory=list)
    trace_name: str | None = Field(default=None)

    _trace: Trace | None
    _event_id_map: dict[int, TraceNode]

    injected_trace_names: list[str] = Field(default_factory=list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trace = None
        self._event_id_map = {}

    def register_state(self):
        """Register this state to receive updates."""
        print("Registering state")
        streamed_traced_singleton.register_state(self)
        self.injected_trace_names = list(streamed_traced_singleton.traces.keys())

    def reset_graph(self):
        self._trace = None
        self.trace_name = None
        return self.update_flame_graph

    def load_default_flame_graph(self):
        self._trace = load_example_trace()
        self.trace_name = None
        self.mark_dirty()
        return self.update_flame_graph

    async def handle_trace_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of a file.

        Args:
            files: The uploaded file.
        """
        print(f"Received file upload {files}")
        assert len(files) == 1, "Expected exactly one file"
        file = files[0]
        upload_data = await file.read()
        self._trace = Trace.parse_raw(upload_data)  # type: ignore
        self.trace_name = None
        return self.update_flame_graph

    def update_flame_graph(self):
        if self._trace is None:
            self.flame_graph_data = FlameGraphNode(name="", value=1, background_color="#00000000", children=[]).dict()
            self._event_id_map = {}
        else:
            self._event_id_map = self._trace.build_event_id_map()
            self.flame_graph_data = convert_trace_to_flame_graph_data(self._trace)
        # is there a current node?
        if self.current_node:
            event_id = self.current_node[-1].event_id
            if event_id in self._event_id_map:
                self._set_current_node(self, event_id)
            else:
                self.current_node = []
        self.mark_dirty()

    def on_injected_trace(self, trace_name: str):
        """Handle an injected trace event."""
        # parse trace_name as json
        trace_name = json.loads(trace_name)

        self.injected_trace_names = list(streamed_traced_singleton.traces.keys())

        if self._trace is None:
            self.trace_name = trace_name

        if self.trace_name == trace_name:
            self._trace = streamed_traced_singleton.traces.get(trace_name, None)  # type: ignore
            self.mark_dirty()

            return self.update_flame_graph

    def handle_trace_selection(self, trace_name: str):
        """Handle the selection of a trace."""
        self.trace_name = trace_name
        self._trace = streamed_traced_singleton.traces.get(trace_name, None)  # type: ignore
        if self._trace is None:
            print(f"Could not find trace {trace_name}")
        self.mark_dirty()

        return self.update_flame_graph

    def update_current_node(self, chart_data: dict):
        node_id = chart_data["source"].get("id", None)
        if node_id is None:
            event_id = None
        else:
            event_id = int(node_id)
        self._set_current_node(self, event_id)

    def _set_current_node(self, event_id: int | None):
        if event_id is None:
            self.current_node = []
        else:
            trace_node = self._event_id_map[event_id]

            properties = trace_node.properties.copy()
            exception = properties.pop("exception", None)
            arguments = properties.pop("arguments", None)
            result = properties.pop("result", None)
            if arguments:
                assert isinstance(arguments, dict)
                arguments = arguments.copy()
                self_object = arguments.pop("self", None)
            else:
                self_object = None

            optional_properties = properties if properties else None
            self.current_node = [
                NodeInfo(
                    node_name=trace_node.name,
                    kind=trace_node.kind,
                    event_id=trace_node.event_id,
                    start_time_ms=trace_node.start_time_ms,
                    end_time_ms=trace_node.end_time_ms,
                    properties=optional_properties,
                    exception=exception,
                    self_object=self_object,
                    result=result,
                    arguments=arguments,
                )
            ]
        self.mark_dirty()


def render_node_info(node_info: NodeInfo):
    """Renders node_info as a simple table."""
    header_style = dict(width="20%", text_align="right", vertical_align="top")

    return rx.table_container(
        rx.table(
            rx.tbody(
                rx.tr(
                    rx.th("Name", style=header_style),
                    rx.td(node_info.node_name, colspan=0),
                ),
                rx.tr(
                    rx.th("", style=header_style),
                    rx.td(
                        rx.stat_group(
                            rx.stat(
                                rx.stat_number(node_info.kind),
                                rx.stat_help_text("KIND"),
                            ),
                            rx.stat(
                                rx.stat_number((node_info.end_time_ms - node_info.start_time_ms) / 1000),
                                rx.stat_help_text("DURATION (S)"),
                            ),
                            width="100%",
                        )
                    ),
                ),
                rx.cond(
                    node_info.exception,
                    rx.tr(
                        rx.th("Exception", style=header_style),
                        rx.td(json_view(data=node_info.exception), colspan=0),
                    ),
                ),
                rx.cond(
                    node_info.result,
                    rx.tr(
                        rx.th("Result", style=header_style),
                        rx.td(json_view(data=node_info.result), colspan=0),
                    ),
                ),
                rx.cond(
                    node_info.arguments,
                    rx.tr(
                        rx.th("Arguments", style=header_style),
                        rx.td(json_view(data=node_info.arguments), colspan=0),
                    ),
                ),
                rx.cond(
                    node_info.self_object,
                    rx.tr(
                        rx.th("Self", style=header_style),
                        rx.td(json_view(data=node_info.self_object), colspan=0),
                    ),
                ),
                rx.cond(
                    node_info.properties,
                    rx.tr(
                        rx.th("Properties", style=header_style),
                        rx.td(json_view(data=node_info.properties), colspan=0),
                    ),
                ),
            ),
            variant="simple",
        ),
        style=dict(width=1024),
    )


@typing.no_type_check
def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.span(
                rx.heading("Trace Viewer", level=1, style=dict(display="inline-block", margin_right="16px")),
                rx.popover(
                    rx.popover_trigger(rx.button(rx.icon(tag="hamburger"), style=dict(vertical_align="top"))),
                    rx.popover_content(
                        rx.popover_header("Choose Trace Source"),
                        rx.popover_body(
                            rx.button("Load Example", on_click=State.load_default_flame_graph),
                            rx.divider(margin="0.5em"),
                            rx.upload(
                                rx.text("Drag and drop files here or click to select trace json file."),
                                border="1px dotted",
                                padding="2em",
                                margin="0.25em",
                            ),
                            rx.button("Load", on_click=lambda: State.handle_trace_upload(rx.upload_files())),
                            rx.divider(margin="0.5em"),
                            rx.select(
                                State.injected_trace_names,
                                is_disabled=State.injected_trace_names.length() == 0,
                                value=State.trace_name,
                                placeholder="Select an available trace",
                                on_change=State.handle_trace_selection,
                            ),
                            rx.divider(margin="0.5em"),
                            rx.button("Reset", on_click=State.reset_graph),
                        ),
                        # pc.popover_footer(pc.text("Footer text.")),
                        rx.popover_close_button(),
                    ),
                ),
            ),
            rx.cond(
                State.flame_graph_data,
                rx.fragment(
                    rx.box(
                        flame_graph(
                            width=1024,
                            height=256,
                            data=State.flame_graph_data,
                            on_change=lambda data: State.update_current_node(data),  # type: ignore
                        ),
                        border="1px orange solid",
                    ),
                    rx.foreach(
                        State.current_node,
                        render_node_info,
                    ),
                ),
            ),
        ),
        padding_top="64px",
        padding_bottom="64px",
    )


streamed_traced_singleton = StreamedTracesSingleton()

meta = [
    {"name": "theme_color", "content": SolarizedColors.green},
    {"char_set": "UTF-8"},
    # {"property": "og:url", "content": "url"},
]

# Add state and page to the app.
app = rx.App(
    state=State,
    stylesheets=[
        'react-json-view-lite.css',
    ],
)
app.add_page(
    index,
    on_load=State.register_state,
    meta=meta,
    title="Trace Viewer",
    description="View traces (both offline and streamed).",
)


@app.api.post("/trace/{trace_name}", status_code=status.HTTP_204_NO_CONTENT)
async def inject_trace(trace_name: str, trace: Trace):
    streamed_traced_singleton.update_trace(trace_name, trace)


app.compile()

if __name__ == "__main__":
    cli.main()
