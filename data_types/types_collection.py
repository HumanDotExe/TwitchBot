from enum import Enum


class ChatMessageType(Enum):
    NORMAL = "normal"
    FIRST_TIME = "first_time"
    ANNOUNCEMENT = "announcement"
    COMMAND = "command"


class NotificationType(Enum):
    SUB = "subscription"
    FOLLOW = "follow"


class EventSubType(Enum):
    CHANNEL_UPDATE = 1
    CHANNEL_FOLLOW = 2
    CHANNEL_SUBSCRIBE = 3
    CHANNEL_SUBSCRIPTION_END = 4
    CHANNEL_SUBSCRIPTION_GIFT = 5
    CHANNEL_SUBSCRIPTION_MESSAGE = 6
    CHANNEL_CHEER = 7
    CHANNEL_RAID = 8
    CHANNEL_BAN = 9
    CHANNEL_UNBAN = 10
    CHANNEL_MODERATOR_ADD = 11
    CHANNEL_MODERATOR_REMOVE = 12
    CHANNEL_POINTS_CUSTOM_REWARD_ADD = 13
    CHANNEL_POINTS_CUSTOM_REWARD_UPDATE = 14
    CHANNEL_POINTS_CUSTOM_REWARD_REMOVE = 15
    CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION_ADD = 16
    CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION_UPDATE = 17
    CHANNEL_POLL_BEGIN = 18
    CHANNEL_POLL_PROGRESS = 19
    CHANNEL_POLL_END = 20
    CHANNEL_PREDICTION_BEGIN = 21
    CHANNEL_PREDICTION_PROGRESS = 22
    CHANNEL_PREDICTION_LOCK = 23
    CHANNEL_PREDICTION_END = 24
    DROP_ENTITLEMENT_GRANT = 25
    EXTENSION_BITS_TRANSACTION_CREATE = 26
    GOALS_BEGIN = 27
    GOALS_PROGRESS = 28
    GOALS_END = 29
    HYPE_TRAIN_BEGIN = 30
    HYPE_TRAIN_PROGRESS = 31
    HYPE_TRAIN_END = 32
    STREAM_ONLINE = 33
    STREAM_OFFLINE = 34
    USER_AUTHORIZATION_GRANT = 35
    USER_AUTHORIZATION_REVOKE = 36
    USER_UPDATE = 37


class PubSubType(Enum):
    CHAT_MODERATOR_ACTIONS = 0


class ModerationActionType(Enum):
    CLEAR = "clear"
    BAN = "ban"
    UNBAN = "unban"


class BeatSaberMessageType(Enum):
    NEXT_SONG = 0
    QUEUE_OPEN = 1
    QUEUE_CLOSE = 2
    SONG_REMOVED = 3
    QUEUE_CLOSED = 4
    QUEUE_OPENED = 5
    SONG_ADDED = 6
    SONG_ADDED_TOO_MANY_RESULTS = 7
    SONG_ADDED_NOT_FOUND = 8
    SONG_ADDED_QUEUE_CLOSED = 9


class ChatBotModuleType(Enum):
    BASE = "chat_bot.base_commands"
    CUSTOM = "chat_bot.custom_commands"
    MOD = "chat_bot.mod_commands"
    BEATSABER = "chat_bot.beatsaber_commands"


class InvalidDataException(Exception):
    pass


class ConfigErrorException(Exception):
    pass


class ValidationException(Exception):
    pass
