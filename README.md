# twitchhacksonline
Bot for 'Twitch Hacks X' streams


## What is it?

The bot takes emotes written in twitch chat and sends it to a keyboard server (listener) that types keys


## Installation

Pre-requisites:
python 3.7+
python3-pip

1. Install dependancies with: `pip install -r requirements.txt`

2. Fill in settings.py with your API keys and such.
    You need a twitch account for the bot and a streamlabs account to receive information about donations/cheers etc.

3. The emote translation is setup in the ./state/saved/emotes.csv file
    You can make a new random emote selection by using the ./state/saved/randomize.py script


