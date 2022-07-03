from __future__ import annotations

from datetime import datetime

from data_types.stream_overlay.types import ChatMessageType


class ChatMessage:
    __global_emotes = {}
    __global_badges = {}

    @classmethod
    def set_global_emotes(cls, emotes: dict):
        cls.__global_emotes = {}
        if 'data' in emotes:
            for emote in emotes['data']:
                cls.__global_emotes[emote['id']] = {k: emote[k] for k in set(list(emote.keys())) - {"id"}}

    @classmethod
    def set_global_badges(cls, badges: dict):
        cls.__global_badges = {}
        if 'data' in badges:
            for badge in badges['data']:
                versions = {}
                for version in badge['versions']:
                    versions[version['id']] = {k: version[k] for k in set(list(version.keys())) - {"id"}}
                cls.__global_badges[badge['set_id']] = versions

    def __init__(self, message: str, timestamp: datetime, tags: dict):
        self.__user = tags['display-name']
        self.__sent_at = timestamp
        self.__user_with_badges = self.format_user(tags)
        if 'first-msg' in tags and tags['first-msg'] == '1':
            self.__type = ChatMessageType.FIRST_TIME
        else:
            self.__type = ChatMessageType.NORMAL
        self.__is_deleted = False
        self.__message = self.format_message(message)
        self.__message_with_emotes = self.replace_twitch_emotes(self.__message, tags)

    def __eq__(self, other):
        return isinstance(other, ChatMessage) and self.__user == other.__user and self.__message == other.__message and self.__sent_at == other.__sent_at

    def to_dict(self):
        if isinstance(self, ChatMessage):
            message_dict = {
                "sent_at": str(self.__sent_at),
                "is_deleted": self.__is_deleted,
                "message": self.__message,
                "type": self.__type.name,
                "message_formatted": self.chat_message,
                "user": self.__user
            }
            return message_dict
        else:
            type_name = self.__class__.__name__
            raise TypeError("Unexpected type {0}".format(type_name))

    @property
    def chat_message(self):
        if self.__type == ChatMessageType.COMMAND:
            return f"{self.__user_with_badges} <i>{self.__message_with_emotes}</i>"
        return f"{self.__user_with_badges}: {self.__message_with_emotes}"

    @property
    def deleted(self):
        return self.__is_deleted

    @property
    def user(self):
        return self.__user

    @property
    def message(self):
        return self.__message

    @property
    def sent_at(self):
        return self.__sent_at

    def format_message(self, message: str):
        if 'ACTION' in message:
            message = message.replace('ACTION ', '')
            message = message.replace('', '')
            self.__type = ChatMessageType.COMMAND
        return message

    def delete(self):
        self.__is_deleted = True

    @classmethod
    def format_user(cls, tags: dict):
        user = ""
        badges = tags['badges'].split(',')
        if len(badges) > 0 and len(cls.__global_badges) > 0:
            user_badges = ""
            for badge in badges:
                key, version = badge.split('/')
                if key in cls.__global_badges and str(version) in cls.__global_badges[key]:
                    user_badges += f"<img id='badge' src='{cls.__global_badges[key][str(version)]['image_url_1x']}'>"
            if len(user_badges) > 0:
                user += f"<span id='badges'>{user_badges}</span>"

        user += f"<span style='color:{tags['color']}'><b>{tags['display-name']}</b></span>"
        return user

    @classmethod
    def replace_twitch_emotes(cls, message: str, tags: dict):
        if len(tags['emotes']) > 0:
            emotes = tags['emotes'].split("/")
            replace = {}
            for emote in emotes:
                emote_parts = emote.split(":")
                if emote_parts[0] in cls.__global_emotes:
                    current_emote = cls.__global_emotes[emote_parts[0]]
                    replace[current_emote['name']] = current_emote['images']['url_1x']
                else:
                    for part in emote_parts[1].split(","):
                        from_str, to_str = part.split("-")
                        name = message[int(from_str):int(to_str) + 1]
                        url = f"https://static-cdn.jtvnw.net/emoticons/v2/{emote_parts[0]}/default/light/1.0"
                        replace[name] = url

            for name, url in replace.items():
                message = message.replace(name, f"<img src='{url}'>")

        return message
