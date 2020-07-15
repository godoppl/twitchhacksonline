# "Twitch Hacks Online"
# 2020 - Frank Godo

import os
import csv
import json
import pathlib
import logging
import random
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

SAVED_FILES_DIR = 'saved'
EMOTES = 'emotes.csv'
EVENTS = 'recent_events.txt'
DONATIONS = 'donations.txt'
UNCOVERED = 'uncovered.txt'
TASK = 'task.txt'
KEYBOARD = '../emotes/keyboard.jpg'


class Emote():
    def __init__(self, emote_id, name, key, scan_code, modifier, image_path, pos_x, pos_y, uncovered, key_width):
        self.emote_id = int(emote_id)
        self.name = name
        self.key = key
        self.scan_code = int(scan_code)
        self.modifier = bool(int(modifier))
        self.image_path = image_path
        self.image_pos = (int(pos_x), int(pos_y))
        self.uncovered = bool(int(uncovered))
        self.key_width = int(key_width)
        # if self.emote_id and not self.image_path:
        #     self.download(3)

    def __str__(self):
        return f"{self.name} = [{self.key}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.scan_code == other.scan_code

    def __lt__(self, other):
        return self.scan_code < other.scan_code

    def get_url(self, size=3):
        # Please note that emotes have Copyright
        return f"https://static-cdn.jtvnw.net/emoticons/v1/{self.emote_id}/{size}.0"

    def download(self, image_size):
        try:
            response = requests.get(self.get_url())
            logging.debug("Dowloaded %d bytes", len(response.content))
            image_path = self.get_image_path(image_size)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, 'bw+') as image_file:
                logging.info("Saving image to %s", image_path)
                image_file.write(response.content)
                self.image_path = image_path
        except AttributeError:
            logger.error("Could not save image file for emote %s", self.name)

    def get_image_path(self, size=3):
        path = pathlib.Path(__file__).parent.absolute()
        image_path = os.path.join(path, f"emotes/{self.emote_id}/{size}.0")
        return image_path

    def to_list(self):
        return [self.emote_id, self.name, self.key, self.scan_code,
                int(self.modifier), self.image_path, self.image_pos[0],
                self.image_pos[1], int(self.uncovered), int(self.key_width)]

class State():
    def __init__(self, user_id, client_id, follower_modulo=5):
        self.path = pathlib.Path(__file__).parent.absolute()
        self.path = os.path.join(self.path, SAVED_FILES_DIR)
        self.followers = 0
        self.user_id = user_id
        self.client_id = client_id
        self.follower_modulo = follower_modulo  # For unlocking emotes every X follower
        self.emotes = dict()
        self.unassigned = list()
        self.uncovered_emotes = set()
        self.choices = []
        self.read_emotes()

    def read_emotes(self):
        """
        Read the emotes state from file
        """
        with open(os.path.join(self.path, EMOTES), 'r') as emotes_file:
            emotes = csv.reader(emotes_file)
            try:
                data = dict()
                unassigned = list()
                uncovered = set()
                for row in emotes:
                    emote = Emote(*row)
                    if int(emote.emote_id) == 0:
                        unassigned.append(emote)
                    else:
                        data[emote.name] = emote
                        if emote.uncovered:
                            uncovered.add(emote.name)
                self.emotes = data
                logger.debug("Read %d emotes from file", len(data))
                self.unassigned = unassigned
                logger.debug("%s emotes are unassigned", len(unassigned))
                self.uncovered_emotes = uncovered
            except ValueError:
                logger.error("Error in %s, discarded read", EMOTES)

    def write_emotes(self):
        """
        Write the emotes state to file
        """
        logger.info("Writing %d emotes to %s", len(self.emotes), EMOTES)
        with open(os.path.join(self.path, EMOTES), 'w+') as emotes_file:
            writer = csv.writer(emotes_file)
            emotes = list(self.emotes.values())
            emotes.extend(list(self.unassigned))
            for emote in sorted(emotes):
                writer.writerow(emote.to_list())
                if emote.uncovered:
                    self.uncovered_emotes.add(emote.name)
        self.write_uncovered()

    def get_emote_by_key(self, key, only_if_uncovered=True):
        """
        Get emote object that corresponds with key
        """
        for obj in self.emotes.values():
            if obj.key == key.replace('-', ' '):
                logger.debug("Key %s matched!", key)
                if only_if_uncovered and not obj.uncovered:
                    break
                else:
                    return obj
        return None

    def get_emote(self, emote, only_if_uncovered=True):
        """
        Get emote object from emote name
        """
        try:
            obj = self.emotes[emote]
            if only_if_uncovered and not obj.uncovered:
                return None
            else:
                return obj
        except KeyError:
            return None

    def get_keys(self, text, uncover=False):
        """
        Pick out emotes from text and return keys that correspond
        """
        if isinstance(text, str):
            text = text.split()
        keys = []
        modifier = False
        for emote in text:
            try:
                obj = self.emotes.get(emote)
                if uncover and obj.name not in self.uncovered_emotes:
                    self.uncover_emotes([obj.name])
                if modifier:
                    keys[-1] = keys[-1] + "+" + obj.key
                else:
                    keys.append(obj.key)
                modifier = obj.modifier
            except (KeyError, AttributeError):
                continue
        return keys

    def generate_keyboard(self):
        # This writes the text representation of the emote to the keyboard layout
        try:
            keyboard = Image.open(os.path.join(self.path, KEYBOARD)).convert('RGBA')
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            logger.info("Generating new keyboard layout")
        except (FileNotFoundError, OSError):
            logger.error("Could not generate keyboard layout")
        for emote in self.uncovered_emotes:
            try:
                obj = self.emotes.get(emote)
                textbox = Image.new('RGBA', (obj.key_width,140), (0,0,0,0))
                d = ImageDraw.Draw(textbox)
                wrapped = "\n".join(textwrap.wrap(obj.name, width=obj.key_width//16))
                d.multiline_text((0,0), wrapped, font=font, fill=(255,255,255,255), spacing=4)
                keyboard.paste(textbox, obj.image_pos, textbox)
            except ValueError:
                logger.error("Failed to add text of %d: %s", obj.emote_id, obj.name)
        path = os.path.join(self.path, 'keyboard.jpg')
        keyboard.convert('RGB').save(path)

    def write_uncovered(self):
        """
        Write list of uncovered keys to file
        (For OBS overlay and twitch chat)
        """
        with open(os.path.join(self.path, UNCOVERED), 'w+') as uncovered:
            logger.debug("Writing uncovered keys to file")
            lines = []
            for emote in self.uncovered_emotes:
                obj = self.get_emote(emote, True)
                if obj:
                    lines.append(str(obj))
            logger.debug("Uncovered keys: %s", lines)
            uncovered.write(" | ".join(lines))
        self.generate_keyboard()

    def list_uncovered_keys(self):
        """
        Read the list of uncovered keys (from file)
        """
        return open(os.path.join(self.path, UNCOVERED), 'r').read()

    def next_task(self):
        """
        Read the next task (from file)
        """
        return open(os.path.join(self.path, TASK), 'r').read()

    def uncover_random_emote(self):
        """
        Uncovers a random emote and writes the state to disk
        If all emotes have already been uncovered, it returns a message
        """
        if len(self.uncovered_emotes) == len(self.emotes.keys()):
            return "All keys have already been uncovered"
        drawing = True
        choice = None
        while drawing:
            choice = random.choice(list(self.emotes.values()))
            drawing = choice.uncovered
        choice.uncovered = True
        self.emotes[choice.name] = choice
        self.write_emotes()
        return choice

    def uncover_emotes(self, emotes):
        """
        Uncover a specific emote and write state to disk
        """
        objects = []
        for emote in emotes:
            obj = self.get_emote(emote, False)
            if not obj:
                continue
            if not obj.uncovered:
                obj.uncovered = True
                self.emotes[emote] = obj
            objects.append(obj)
        self.write_emotes()
        return objects

    def uncover_keys(self, keys):
        """
        Uncover an emote corresponding to a specific key, write state to disk
        """
        objects = []
        for key in keys:
            logger.debug("Looking to uncover: %s", key)
            obj = self.get_emote_by_key(key, False)
            if not obj:
                logger.debug("Could not find: %s", key)
                continue
            if not obj.uncovered:
                logger.debug("Uncovering: %s", key)
                obj.uncovered = True
                self.emotes[obj.name] = obj
            objects.append(obj)
        self.write_emotes()
        return objects

    def cover_keys(self, keys):
        """
        Cover a key back up, write state to disk
        """
        objects = []
        for key in keys:
            obj = self.get_emote_by_key(key, False)
            if not obj:
                continue
            if obj.uncovered:
                obj.uncovered = False
                self.emotes[obj.name] = obj
                self.uncovered_emotes.remove(obj.name)
            objects.append(obj)
        self.write_emotes()
        return objects

    def get_user(self, user_id):
        pass

    def fetch_follow_count(self):
        url = f'https://api.twitch.tv/kraken/channels/{self.user_id}/follows'
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': self.client_id}
        response = requests.get(url, headers=headers)
        try:
            followers = json.loads(response.content)
            self.followers = int(followers.get('_total'))
            # self.followers = [follow.get('user').get('name') for follow in followers.get('follows')]
        except (KeyError, TypeError):
            logger.exception("Failed to parse followers")

    def update_event(self, followers=None, donation=None):
        """
        Update the recent events file (used for OBS)
        """
        if donation:
            logger.info("New donation: %s", donation)
            with open(os.path.join(self.path, EVENTS), 'w+') as f:
                f.write("Last donation: " + donation)
            with open(os.path.join(self.path, DONATIONS), 'a') as donation_file:
                donation_file.write(donation + "\n")
        # Uncomment this code if you want every X new follower to unlock a random key
        # elif followers:
        #     mod = self.follower_modulo
        #     remaining = mod - (followers % mod)
        #     if remaining == 1:
        #         text = f"Next follower uncovers another key!"
        #     else:
        #         text = f"{remaining} follower(s) left until another key is uncovered"
        #     if remaining == mod:
        #         self.uncover_random_emote()
        #     self.followers = followers
        #     with open(os.path.join(self.path, EVENTS), 'w+') as f:
        #         f.write(text)
