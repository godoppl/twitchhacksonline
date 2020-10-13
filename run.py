#!/usr/bin/env python3
#
# twitchhacks.online
# "Twitch Hacks Online"
# 2020 - Frank Godo

import logging
import cmd
from twitchbot import TwitchBot
from settings import LOG_FILE, LOGGING_LEVEL, MACHINE_NAME

logging.basicConfig(filename=LOG_FILE, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


class TwitchBotShell(cmd.Cmd):
    intro = 'Interactive Twitch Bot'
    prompt = '> '

    def __init__(self, bot):
        self.bot = bot
        self.__init__()

    def do_help(self, args):
        print("""
            Commands:
            help - This help text
            connect - Connect to the twitch IRC and WS services
            ls - list the challenges (Not implemented)
            status - Show current challenge
            start - Start the current challenge VM
            stop [save] - Stop the current challenge VM (and save current state)
            challenge - Switch to a different challenge (Not implemented)
            stream (up|down) - Start or stop the stream (Not implemented)
            quit - Shut down the stream and quit the bot
        """)

    def do_connect(self, args):
        print("Not implemented.... yet..")
        # Maybe use bot.start() and watch it yourself?
        # self.bot.run() # Run threaded?

    def do_ls(self, args):
        print("Not implemented.... yet..")

    def do_status(self, args):
        status = "online" if self.bot.box.is_running() else "offline"
        print(f"{MACHINE_NAME} is {status}")

    def do_start(self, args):
        if self.bot.box.is_running():
            print(f"Starting {MACHINE_NAME}...")
            self.bot.box.launch()
            print("Started")
        else:
            print(f"{MACHINE_NAME} is already running")

    def do_stop(self, args):
        save = "save" in args
        if self.bot.box.is_running():
            print(f"{MACHINE_NAME} is already stopped")
        else:
            print(f"Stopping {MACHINE_NAME}...")
            self.bot.box.shut_down(save=save)

    def do_challenge(self, args):
        print("Not implemented.... yet..")

    def do_stream(self, args):
        print("Not implemented.... yet..")

    def do_quit(self, args):
        # TODO: Disconnect the bot
        self.close()
        return True


def main():
    bot = TwitchBot()
    return TwitchBotShell(bot).cmdloop()


if __name__ == '__main__':
    main()
