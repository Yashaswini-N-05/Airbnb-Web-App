from collections.abc import Mapping
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


tracer = trace.get_tracer(__name__)


def set_span_attributes(span, attributes: Mapping[str, Any]) -> None:
    if span is None or not span.is_recording():
        return
    for key, value in attributes.items():
        if value is not None:
            span.set_attribute(key, value)


def add_span_event(span, event_name: str, attributes: Mapping[str, Any] | None = None) -> None:
    if span is None or not span.is_recording():
        return
    span.add_event(event_name, attributes or {})


def record_span_exception(span, exc: Exception) -> None:
    if span is None or not span.is_recording():
        return
    span.record_exception(exc)
    span.set_status(Status(StatusCode.ERROR))
