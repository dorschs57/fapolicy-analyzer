from fapolicy_analyzer import Changeset
from redux import Action, Reducer, handle_actions
from typing import Sequence, cast
from fapolicy_analyzer.ui.actions import (
    ADD_CHANGESETS,
    CLEAR_CHANGESETS,
)


def handle_add_changesets(
    state: Sequence[Changeset], action: Action
) -> Sequence[Changeset]:
    payload = cast(tuple[Changeset], action.payload)
    return (*state, *payload)


def handle_clear_changesets(
    state: Sequence[Changeset], action: Action
) -> Sequence[Changeset]:
    return state[:-1]


changeset_reducer: Reducer = handle_actions(
    {
        ADD_CHANGESETS: handle_add_changesets,
        CLEAR_CHANGESETS: handle_clear_changesets,
    },
    [],
)