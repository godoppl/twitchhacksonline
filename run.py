#!/usr/bin/env python3
#
# twitchhacks.online
# "Twitch hacks X"
# 2020 - Frank Godo

import logging
import socketio
from twitchbot import TwitchBot
from state import State
from settings import WS_TOKEN, USER_ID, CLIENT_ID, KEYBOARD_HOST, LOG_FILE, LOGGING_LEVEL
from kbd_client import KbdClient

logging.basicConfig(filename=LOG_FILE, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    state = State(USER_ID, CLIENT_ID)
    wk = KbdClient(KEYBOARD_HOST)
    bot = TwitchBot(state, wk)
    if WS_TOKEN:
        logger.info("Websocket starting...")
        sio = socketio.Client()

        @sio.event
        def connect():
            print('StreamLabs websocket connected')

        @sio.event
        def event(data):
            try:
                if data.get('type') == 'donation':
                    donations = data.get('message')
                    for donation in donations:
                        amount, currency = float(donation.get('amount')), donation.get('currency')
                        message, name = donation.get('message'), donation.get('name')
                        print("Received donation:", currency, amount, message, name)
                        text = None
                        if 0.99 < amount < 2.0:
                            uncovered = state.uncover_random_emote()
                            text = f"{name} uncovered: {uncovered}"
                        elif 1.99 < amount < 10.0:
                            key = message.split()[0]
                            uncovered = state.uncover_keys([key])
                            text = f"{name} uncovered: {uncovered}"
                        elif 9.99 < amount:
                            wk.send_command(str(message))
                            text = f"{name} ran command: {message}"
                        if text:
                            state.update_event(donation=text)
                elif data.get('type') == 'bits':
                    cheers = data.get('message')
                    for cheer in cheers:
                        amount = int(cheer.get('amount'))
                        message, name = cheer.get('message'), cheer.get('name')
                        print("Received cheer:", amount, message, name)
                        text = None
                        if amount < 50:
                            text = f"{name} cheered {amount} bits!"
                        elif 49 < amount < 100:
                            uncovered = state.uncover_random_emote()
                            text = f"{name} uncovered: {uncovered}"
                        elif 99 < amount < 1000:
                            key = message.split()[0]
                            uncovered = state.uncover_keys([key])
                            text = f"{name} uncovered: {uncovered}"
                        elif 999 < amount:
                            wk.send_command(str(message))
                            text = f"{name} ran command: {message}"
                        if text:
                            state.update_event(donation=text)
            except KeyError as e:
                print("Could not decode message")
                print(e)

        @sio.event
        def disconnect():
            print('disconnected from server')

        sio.connect(f'https://sockets.streamlabs.com?token={WS_TOKEN}')
    bot.run()


if __name__ == '__main__':
    main()
