from contextlib import contextmanager

import wandb.sdk.wandb_run
from wandb.sdk.data_types import trace_tree

from llmtracer import Trace, TraceNode, TraceNodeKind, build_trace, module_filtering  # type: ignore


def convert_event_kind_str(kind: TraceNodeKind):
    try:
        span_kind = trace_tree.SpanKind(kind.value)
    except ValueError:
        span_kind = trace_tree.SpanKind.AGENT

    return span_kind


def convert_result(result: object):
    if result is None:
        return None
    if isinstance(result, dict | list | set):
        return result
    return [result]


def build_span(node: TraceNode):
    span = trace_tree.Span()
    span.span_id = str(node.event_id)
    span.name = node.name if node.name is not None else ''
    span.span_kind = convert_event_kind_str(node.kind)

    span.start_time_ms = node.start_time_ms
    span.end_time_ms = node.end_time_ms

    if "exception" not in node.properties:
        span.status_code = trace_tree.StatusCode.SUCCESS
    else:
        span.status_code = trace_tree.StatusCode.ERROR
        span.status_message = repr(node.properties["exception"])

    span.add_named_result(
        node.properties.get('arguments', {}), convert_result(node.properties.get('result', None))  # type: ignore
    )

    properties = dict(node.properties)
    if "arguments" in properties:
        del properties["arguments"]
    if "result" in properties:
        del properties["result"]

    span.attributes = dict(
        properties=properties,
        delta_stack=node.delta_frame_infos,
    )
    span.child_spans = [build_span(child) for child in node.children]
    return span


def wandb_build_trace_trees(trace: Trace):
    media_list = []
    for trace_instance in trace.traces:
        scope_span = build_span(trace_instance)

        media = trace_tree.WBTraceTree(root_span=scope_span, model_dict=trace.unique_objects)
        media_list.append(media)
    return media_list


@contextmanager
def wandb_tracer(
    name: str | None,
    *,
    module_filters: module_filtering.ModuleFiltersSpecifier | None = None,
    stack_frame_context: int = 3,
):
    tb = build_trace(
        module_filters=module_filters, stack_frame_context=stack_frame_context, name=wandb.run.name  # type: ignore
    )  # type: ignore
    try:
        with tb.scope(name) as builder:
            yield builder
    finally:
        for trace_artifact in wandb_build_trace_trees(builder.build()):
            wandb.log({"trace": trace_artifact})  # type: ignore
        wandb.finish()  # type: ignore
