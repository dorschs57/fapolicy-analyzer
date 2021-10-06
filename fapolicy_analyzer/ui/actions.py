from enum import Enum
from fapolicy_analyzer import Changeset, Event, Group, Trust, User
from itertools import count
from redux import Action, create_action
from typing import Any, Iterator, NamedTuple, Sequence

ADD_NOTIFICATION = "ADD_NOTIFICATION"
REMOVE_NOTIFICATION = "REMOVE_NOTIFICATION"

SET_SYSTEM_CHECKPOINT = "SET_SYSTEM_CHECKPOINT"
RESTORE_SYSTEM_CHECKPOINT = "RESTORE_SYSTEM_CHECKPOINT"

ADD_CHANGESETS = "ADD_CHANGESETS"
APPLY_CHANGESETS = "APPLY_CHANGESETS"
CLEAR_CHANGESETS = "CLEAR_CHANGESET"

REQUEST_ANCILLARY_TRUST = "REQUEST_ANCILLARY_TRUST"
RECEIVED_ANCILLARY_TRUST = "RECEIVED_ANCILLARY_TRUST"
ERROR_ANCILLARY_TRUST = "ERROR_ANCILLARY_TRUST"

REQUEST_SYSTEM_TRUST = "REQUEST_SYSTEM_TRUST"
RECEIVED_SYSTEM_TRUST = "RECEIVED_SYSTEM_TRUST"
ERROR_SYSTEM_TRUST = "ERROR_SYSTEM_TRUST"

DEPLOY_ANCILLARY_TRUST = "DEPLOY_ANCILLARY_TRUST"
ANCILLARY_TRUST_DEPLOYED = "ANCILLARY_TRUST_DEPLOYED"
ERROR_DEPLOYING_ANCILLARY_TRUST = "ERROR_DEPLOYING_ANCILLARY_TRUST"

REQUEST_EVENTS = "REQUEST_EVENTS"
RECEIVED_EVENTS = "RECEIVED_EVENTS"
ERROR_EVENTS = "ERROR_EVENTS"

REQUEST_USERS = "REQUEST_USERS"
RECEIVED_USERS = "RECEIVED_USERS"
ERROR_USERS = "ERROR_USERS"

REQUEST_GROUPS = "REQUEST_GROUPS"
RECEIVED_GROUPS = "RECEIVED_GROUPS"
ERROR_GROUPS = "ERROR_GROUPS"


def _create_action(type: str, payload: Any = None) -> Action:
    return create_action(type)(payload)


_ids: Iterator[int] = iter(count())


class NotificationType(Enum):
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    SUCCESS = "success"


class Notification(NamedTuple):
    id: int
    text: str
    type: NotificationType


def add_notification(text: str, type: NotificationType) -> Action:
    return _create_action(ADD_NOTIFICATION, (Notification(next(_ids), text, type)))


def remove_notification(id: int) -> Action:
    return _create_action(REMOVE_NOTIFICATION, (Notification(id, "", None)))


def add_changesets(*changesets: Changeset) -> Action:
    return _create_action(ADD_CHANGESETS, *changesets)


def apply_changesets(*changesets: Changeset) -> Action:
    return _create_action(APPLY_CHANGESETS, changesets)


def clear_changesets() -> Action:
    return _create_action(CLEAR_CHANGESETS)


def request_ancillary_trust() -> Action:
    return _create_action(REQUEST_ANCILLARY_TRUST)


def received_ancillary_trust(trust: Sequence[Trust]) -> Action:
    return _create_action(RECEIVED_ANCILLARY_TRUST, trust)


def error_ancillary_trust(error: str) -> Action:
    return _create_action(ERROR_ANCILLARY_TRUST, error)


def request_system_trust() -> Action:
    return _create_action(REQUEST_SYSTEM_TRUST)


def received_system_trust(trust: Sequence[Trust]) -> Action:
    return _create_action(RECEIVED_SYSTEM_TRUST, trust)


def error_system_trust(error: str) -> Action:
    return _create_action(ERROR_SYSTEM_TRUST, error)


def deploy_ancillary_trust() -> Action:
    return _create_action(DEPLOY_ANCILLARY_TRUST)


def ancillary_trust_deployed() -> Action:
    return _create_action(ANCILLARY_TRUST_DEPLOYED)


def error_deploying_ancillary_trust(error: str) -> Action:
    return _create_action(ERROR_DEPLOYING_ANCILLARY_TRUST, error)


def set_system_checkpoint() -> Action:
    return _create_action(SET_SYSTEM_CHECKPOINT)


def restore_system_checkpoint() -> Action:
    return _create_action(RESTORE_SYSTEM_CHECKPOINT)


def request_events(file: str) -> Action:
    return _create_action(REQUEST_EVENTS, file)


def received_events(events: Sequence[Event]) -> Action:
    return _create_action(RECEIVED_EVENTS, events)


def error_events(error: str) -> Action:
    return _create_action(ERROR_EVENTS, error)


def request_users() -> Action:
    return _create_action(REQUEST_USERS)


def received_users(users: Sequence[User]) -> Action:
    return _create_action(RECEIVED_USERS, users)


def error_users(error: str) -> Action:
    return _create_action(ERROR_USERS, error)


def request_groups() -> Action:
    return _create_action(REQUEST_GROUPS)


def received_groups(groups: Sequence[Group]) -> Action:
    return _create_action(RECEIVED_GROUPS, groups)


def error_groups(error: str) -> Action:
    return _create_action(ERROR_GROUPS, error)