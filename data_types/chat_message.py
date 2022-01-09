class ChatMessage:
    __global_emotes = {}
    __global_badges = {}

    @classmethod
    def set_global_emotes(cls, emotes: dict):
        cls.__global_emotes = {}
        for emote in emotes['data']:
            cls.__global_emotes[emote['id']] = {k: emote[k] for k in set(list(emote.keys())) - {"id"}}

    @classmethod
    def set_global_badges(cls, badges: dict):
        cls.__global_badges = {}
        for badge in badges['data']:
            versions = {}
            for version in badge['versions']:
                versions[version['id']] = {k: version[k] for k in set(list(version.keys())) - {"id"}}
            cls.__global_badges[badge['set_id']] = versions

    def __init__(self, message: str, tags: dict):
        self.__user = tags['display-name']
        self.__user_with_badges = self.format_user(tags)
        self.__message = message
        self.__message_with_emotes = self.replace_twitch_emotes(message, tags)
        self.__time = 60

    @property
    def time_left(self):
        return self.__time

    def decrease_time_left(self):
        self.__time -= 5

    @property
    def chat_message(self):
        return f"{self.__user_with_badges}: {self.__message_with_emotes}"

    @classmethod
    def format_user(cls, tags):
        user = ""
        badges = tags['badges'].split(',')
        if len(badges) > 0:
            user += "<span id='badges'>"
            for badge in badges:
                key, version = badge.split('/')
                user += f"<img id='badge' src='{cls.__global_badges[key][str(version)]['image_url_1x']}'>"
            user += "</span>"

        user += f"<span style='color:{tags['color']}'><b>{tags['display-name']}</b></span>"
        return user

    @classmethod
    def replace_twitch_emotes(cls, message, tags):
        if len(tags['emotes']) > 0:
            emotes = tags['emotes'].split("/")
            replace = {}
            for emote in emotes:
                emote_parts = emote.split(":")
                if emote_parts[0] in cls.__global_emotes:
                    current_emote = cls.__global_emotes[emote_parts[0]]
                    replace[current_emote['name']] = current_emote['images']['url_1x']
                else:
                    from_str, to_str = emote_parts[1].split("-")
                    name = message[int(from_str):int(to_str)+1]
                    url = f"https://static-cdn.jtvnw.net/emoticons/v2/{emote_parts[0]}/default/light/1.0"
                    replace[name] = url

            for name, url in replace.items():
                message = message.replace(name, f"<img src='{url}'>")

        return message
