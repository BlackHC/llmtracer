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

from llmtracer.tools.trace_viewer.app.endpoint_integration import trace_viewer_send_trace_builder
from llmtracer.trace_builder import TraceBuilder, TraceBuilderEventHandler


class TraceViewerIntegration(TraceBuilderEventHandler):
    def on_scope_final(self, builder: 'TraceBuilder'):
        trace_viewer_send_trace_builder(builder, force=True)

    def on_event_scope_final(self, builder: 'TraceBuilder'):
        trace_viewer_send_trace_builder(builder, force=False)
