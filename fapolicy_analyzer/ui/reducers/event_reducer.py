from fapolicy_analyzer.ui.actions import (
    ERROR_EVENTS,
    RECEIVED_EVENTS,
)
from fapolicy_analyzer import Event
from redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast


class EventState(NamedTuple):
    error: str
    events: Sequence[Event]


def _create_state(state: EventState, **kwargs: Optional[Any]) -> EventState:
    return EventState(**{**state._asdict(), **kwargs})


def handle_received_events(state: EventState, action: Action) -> EventState:
    payload = cast(Sequence[Event], action.payload)
    return _create_state(state, events=payload, error=None)


def handle_error_events(state: EventState, action: Action) -> EventState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


event_reducer: Reducer = handle_actions(
    {
        RECEIVED_EVENTS: handle_received_events,
        ERROR_EVENTS: handle_error_events,
    },
    EventState(error=None, events=[]),
)