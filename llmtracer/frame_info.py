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

import inspect

from pydantic import BaseModel

from llmtracer import module_filtering


class FrameInfo(BaseModel):
    """
    A frame info object that is serializable.
    """

    module: str
    lineno: int
    function: str
    code_context: list[str] | None
    index: int | None
    # positions: dis.Positions | None = None


def get_frame_infos(
    num_top_frames_to_skip: int = 0,
    num_bottom_frames_to_skip: int = 0,
    module_filters: module_filtering.ModuleFilters | None = None,
    context: int = 3,
) -> tuple[list[FrameInfo], int]:
    # Get the current stack frame infos
    frame_infos: list[inspect.FrameInfo] = inspect.stack(context=context)

    # Get the stack frame infos for the delta stack summary
    caller_frame_infos = frame_infos[num_top_frames_to_skip + 1 :]

    stack_height = len(caller_frame_infos)

    # remove bottom frames
    relevant_inspect_frame_infos: list[inspect.FrameInfo] = caller_frame_infos[
        : stack_height - num_bottom_frames_to_skip
    ]

    relevant_frame_infos: list[FrameInfo] = [
        FrameInfo(
            module=module.__name__ if (module := inspect.getmodule(f.frame)) else "<unknown>",
            lineno=f.lineno,
            function=f.function,
            code_context=f.code_context,
            index=f.index,
            # positions=f.positions,
        )
        for f in relevant_inspect_frame_infos
    ]

    # Filter the stack frame infos
    if module_filters is not None:
        relevant_frame_infos = [f for f in relevant_frame_infos if module_filters(f.module)]

    return relevant_frame_infos, stack_height


def test_get_frame_infos():
    def f():
        frame_infos = get_frame_infos(module_filters=module_filtering.only_module(__name__))
        assert len(frame_infos) == 3
        assert frame_infos[0].function == "f"
        assert frame_infos[1].function == "g"
        assert frame_infos[2].function == "test_get_frame_infos"

    def g():
        f()

    g()
