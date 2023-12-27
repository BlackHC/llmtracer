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

from .convenience import add_event, build_trace, event_scope, register_object, update_event_properties, update_name
from .handlers.json_writer import JsonFileWriter
from .handlers.trace_viewer import TraceViewerIntegration
from .module_filtering import module_filter, module_filters
from .trace_builder import (
    TraceBuilder,
    TraceBuilderEventHandler,
    trace_calls,
    trace_module_filters,
    trace_object_converter,
)
from .trace_schema import Trace, TraceNode, TraceNodeKind
from .wandb_integration import wandb_build_trace_trees, wandb_tracer

__version__ = '1.2.1'
