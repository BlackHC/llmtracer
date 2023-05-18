from contextlib import contextmanager

from llmtracer import module_filtering, trace_builder, trace_schema


def build_trace(
    module_filters: module_filtering.ModuleFiltersSpecifier | None = None,
    stack_frame_context: int = 3,
    name: str | None = None,
):
    """
    Context manager that allows to trace our program execution.
    """
    if not module_filters:
        module_filters = trace_builder.trace_module_filters

    builder = trace_builder.TraceBuilder(
        module_filters=module_filtering.module_filters(module_filters), stack_frame_context=stack_frame_context
    )
    builder.event_root.name = name
    return builder


def add_event(
    name: str,
    properties: dict[str, object] | None = None,
    kind: trace_schema.TraceNodeKind = trace_schema.TraceNodeKind.EVENT,
):
    """
    Add an event to the current scope.
    """
    current = trace_builder.TraceBuilder.get_current()
    if current is not None:
        current.add_event(name, properties, kind)


def register_object(obj: object, name: str, properties: dict[str, object]):
    """
    Register an object as unique, so that it will be serialized only once.
    """
    current = trace_builder.TraceBuilder.get_current()
    if current is not None:
        current.register_object(obj, name, properties)


def update_event_properties(properties: dict[str, object] | None = None, /, **kwargs):
    """
    Update the properties of the current event.
    """
    current = trace_builder.TraceBuilder.get_current()
    if current is not None:
        current.update_event_properties(properties, **kwargs)


def update_name(name: str):
    """
    Update the name of the current event.
    """
    current = trace_builder.TraceBuilder.get_current()
    if current is not None:
        current.update_name(name)


@contextmanager
def event_scope(
    name: str,
    properties: dict[str, object] | None = None,
    kind: trace_schema.TraceNodeKind = trace_schema.TraceNodeKind.SCOPE,
):
    """
    Context manager that allows to trace our program execution.
    """
    current = trace_builder.TraceBuilder.get_current()
    if current is None:
        yield
    else:
        with current.event_scope(name, properties=properties, kind=kind, skip_frames=2):
            yield
