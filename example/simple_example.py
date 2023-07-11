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
"""
A simple example that does not call LLMs directly but instead showcases capturing and saving traces of nested calls.
"""
from time import sleep

import wandb

from llmtracer import JsonFileWriter, TraceViewerIntegration, trace_calls, wandb_tracer
from llmtracer.handlers.svg_writer import SvgFileWriter


@trace_calls(capture_args=True, capture_return=True)
def add_values(a: int, b: int):
    # sleep 1 second
    sleep(1)

    return a + b


@trace_calls(capture_args=True, capture_return=True)
def fibonacci(n: int):
    if n <= 1:
        return 1
    return add_values(fibonacci(n - 1), fibonacci(n - 2))


wandb.init(project="llmtracer", name="simple_example")

event_handlers = [JsonFileWriter("simple_example.json"), SvgFileWriter("simple_example.svg"), TraceViewerIntegration()]

with wandb_tracer("main", stack_frame_context=0, event_handlers=event_handlers) as trace_builder:
    print(fibonacci(10))
