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
