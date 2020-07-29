# twitchhacks.online
# "Twitch Hacks Online
# 2020 - Frank Godo

import logging

MAX_FREEBIES = 10

# Twitch channel settings
USER_ID = None  # Integer ID of Twitch channel account
CHANNEL_NAME = None
CHANNEL_ID = None  # Integer ID of Twitch channel account
BOT_NICK = None
IRC_TOKEN = None  # Token for Bot user here https://twitchapps.com/tmi/
SUBSCRIPTIONS = [f'channel-bits-events-v2.{CHANNEL_ID}',
                 f'channel-points-channel-v1.{CHANNEL_ID}',
                 f'channel-subscribe-events-v1.{CHANNEL_ID}',
                 f'chat_moderator_actions.{CHANNEL_ID}']

# Twitch Application settings
# Register a new application to get these
# https://dev.twitch.tv/console/apps
CLIENT_ID = None
CLIENT_SECRET = None
CLIENT_TOKEN = None  # Scopes: "bits:read", "channel_subscriptions", "channel:read:redemptions", "channel:moderate"
API_TOKEN = None  # Needed to get follower information

# VirtualBox settings
MACHINE_NAME = None  # Name of the VirtualBox VM


# Logging
LOG_FILE = 'twitchhacks.log'
LOGGING_LEVEL = logging.INFO
