#!/usr/bin/env python3
#
# twitchhacks.online
# "Twitch Hacks Online"
# 2020 - Frank Godo

import logging
from twitchbot import TwitchBot
from settings import LOG_FILE, LOGGING_LEVEL

logging.basicConfig(filename=LOG_FILE, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    bot = TwitchBot()
    bot.run()


if __name__ == '__main__':
    main()
