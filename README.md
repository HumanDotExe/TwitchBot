# TwitchBot
This is a custom twitch chatbot that also functions as a webserver displaying notifications. This project can be considered to be an early beta at most, 
so don't expect it to work perfectly. Also, I will not give support on how to set it up at this point in time. Only use it if you think the information 
in this readme and the code is enough to set it up.

In case you do find something that might be a bug, feel free to report it here and I will look at it. Feature requests can be made but since this bot is 
mainly written for me and my friends I might not add it. If you are looking for a feature complete bot, this is not it.


Here is what is needed to use this:
- An app registered with twitch that you know the id and secret off
- A `secrets.ini` as detailed below in the root path
- A working reverse proxy with a non self signed https certificate (blame twitch, not me)
- At least one twitch account to run this with, it can be your own
- Everyone that you want bans (or other eventsub stuff) to work needs to have the app authorized in their twitch account
  to do so, check out https://pytwitchapi.readthedocs.io/en/latest/modules/twitchAPI.oauth.html for an easy way to do so.

`secrets.ini`
```
[GENERAL]
twitch_callback_url = ADD IN YOUR CALLBACK URL HERE
twitch_callback_port = ADD IN YOUR PORT HERE
monitor_streams = ADD THE STREAM THAT SHOULD BE USED HERE (SEPARATE BY WHITESPACE)
base_folder_name = streams

[APP]
client_id = YOUR TWITCH APP ID
client_secret = YOUR TWITCH APP SECRET

[BOT]
nick = YOUR BOT NAME
prefix = !
chat_oauth = oauth:CHAT TOKEN HERE

[WEBSERVER]
bind_ip = IP OF THE PC THE BOT IS RUNNING ON
bind_port = PORT IT SHOULD USE
```
