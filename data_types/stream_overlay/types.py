from enum import Enum


class ActionType(Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"
    CLEAR = "clear"


class ChatMessageType(Enum):
    NORMAL = "normal"
    FIRST_TIME = "first_time"
    ANNOUNCEMENT = "announcement"
    COMMAND = "command"


class NotificationType(Enum):
    SUB = "subscription"
    FOLLOW = "follow"