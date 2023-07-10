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
import os
from dataclasses import dataclass

from llmtracer.trace_builder import TraceBuilder, TraceBuilderEventHandler


@dataclass
class JsonFileWriter(TraceBuilderEventHandler):
    filename: str

    def on_event_scope_final(self, builder: 'TraceBuilder'):
        trace = builder.build()
        json_trace = trace.dict()

        tempfile = self.filename + ".new_tmp"

        with open(tempfile, "w") as f:
            json.dump(json_trace, f, indent=1)

        os.replace(tempfile, self.filename)
