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

import wandb

from llmtracer import TraceNodeKind, event_scope
from llmtracer.wandb_integration import wandb_tracer

wandb.init(project="blackboard-pagi", name="wandb_integration_test", reinit=True)  # type: ignore

with wandb_tracer("", module_filters="blackboard_pagi.*", stack_frame_context=0):
    with event_scope("foo", kind=TraceNodeKind.AGENT):
        with event_scope("bar", kind=TraceNodeKind.LLM):
            with event_scope("baz", kind=TraceNodeKind.CALL):
                pass
            with event_scope("baz2", kind=TraceNodeKind.CALL):
                pass
        with event_scope("bar2", kind=TraceNodeKind.LLM):
            with event_scope("baz", kind=TraceNodeKind.CALL):
                with event_scope("foo", kind=TraceNodeKind.AGENT):
                    with event_scope("bar", kind=TraceNodeKind.LLM):
                        with event_scope("baz", kind=TraceNodeKind.CALL):
                            pass
                        with event_scope("baz2", kind=TraceNodeKind.CALL):
                            pass
                    with event_scope("bar2", kind=TraceNodeKind.LLM):
                        with event_scope("baz", kind=TraceNodeKind.CALL):
                            with event_scope("foo", kind=TraceNodeKind.AGENT):
                                with event_scope("bar", kind=TraceNodeKind.LLM):
                                    with event_scope("baz", kind=TraceNodeKind.CALL):
                                        pass
                                    with event_scope("baz2", kind=TraceNodeKind.CALL):
                                        pass
                                with event_scope("bar2", kind=TraceNodeKind.LLM):
                                    with event_scope("baz", kind=TraceNodeKind.CALL):
                                        with event_scope("foo", kind=TraceNodeKind.AGENT):
                                            with event_scope("bar", kind=TraceNodeKind.LLM):
                                                with event_scope("baz", kind=TraceNodeKind.CALL):
                                                    pass
                                                with event_scope("baz2", kind=TraceNodeKind.CALL):
                                                    pass
                                            with event_scope("bar2", kind=TraceNodeKind.LLM):
                                                with event_scope("baz", kind=TraceNodeKind.CALL):
                                                    pass
