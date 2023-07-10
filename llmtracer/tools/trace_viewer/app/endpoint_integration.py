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

import time
import typing
from dataclasses import dataclass

import requests

from llmtracer.utils.weakrefs import WeakKeyIdMap

from . import pcconfig

if typing.TYPE_CHECKING:
    from llmtracer import TraceBuilder


@dataclass
class TraceBuilderUpdate:
    token: str
    last_sent_ms: int


# Weak key dictionary from trace to TraceUpdates
_trace_builder_updates: WeakKeyIdMap['TraceBuilder', TraceBuilderUpdate] = WeakKeyIdMap()

_MIN_SEND_INTERVAL_MS = 500


def trace_viewer_send_trace_builder(trace_builder: 'TraceBuilder', force: bool = False):
    """Send a trace to the backend.

    :param trace_buider: The trace to send.
    :param force: If True, send the trace even if it has not been updated.
    """
    # Get the TraceUpdates object for this trace
    trace_updates = _trace_builder_updates.get(trace_builder)
    trace = trace_builder.build()
    if trace_updates is None:
        if trace.name is not None:
            # Use the trace name as the token if it is set
            token = trace.name
        else:
            # Generate a random token based on the current time
            token = str(int(time.time()))

        # Create a new TraceUpdates object if one does not exist
        trace_updates = TraceBuilderUpdate(token=token, last_sent_ms=-_MIN_SEND_INTERVAL_MS)
        _trace_builder_updates[trace_builder] = trace_updates

    now_ms = int(time.time() * 1000)
    if not force:
        # Check if the trace has been updated since the last send
        if now_ms - trace_updates.last_sent_ms < _MIN_SEND_INTERVAL_MS:
            return
    trace_updates.last_sent_ms = now_ms

    url = pcconfig.config.api_url + "/trace/" + trace_updates.token
    payload = trace.dict()
    try:
        requests.post(url, json=payload, timeout=0.05)
    except requests.exceptions.RequestException:
        pass
