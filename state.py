# twitchhacks.online
# "Twitch Hacks Online"
# 2020 - Frank Godo

import pickle
import logging

logger = logging.getLogger(__name__)


class Store:
    def __init__(self):
        self.channel_id = 0
        self.client_id = ''
        self.followers = set()
        self.allowed = set()
        self.rejected = set()
        self.noobs = dict()
        self.hotseat = None


class State:
    def __init__(self, client_id, channel_id):
        try:
            self.load_store(f'{client_id}-{channel_id}')
        except FileNotFoundError:
            logger.error('Could not load file, creating new store')
            self.create_store(client_id, channel_id)

    # region store
    def create_store(self, client_id, channel_id):
        filename = f'{client_id}-{channel_id}.pkl'
        with open(filename, 'wb') as f:
            self.store = Store()
            self.store.channel_id = channel_id
            self.store.client_id = client_id
            pickle.dump(self.store, f)
            logger.info('Created new store as %s', filename)

    def load_store(self, filename):
        filename = filename + '.pkl'
        with open(filename, 'rb') as f:
            self.store = pickle.load(f)
            logger.info('Loaded store from %s', filename)
            logger.debug(self.store.__dict__)

    def save_store(self):
        filename = f'{self.store.client_id}-{self.store.channel_id}.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(self.store, f)
            logger.info('Saved store to %s', filename)
    # endregion store

    def update_noob(self, username):
        freebies = self.store.noobs.get(username.lower(), 0)
        self.store.noobs[username.lower()] = freebies + 1
        self.save_store()
        return freebies

    def hotseat(self, username):
        if username:
            self.store.hotseat = username.lower()
        else:
            self.store.hotseat = None
        self.save_store()

    def get_hotseat(self):
        return self.store.hotseat

    def is_follower(self, username):
        return username.lower() in self.store.followers

    def add_follower(self, username):
        self.store.followers.add(username.lower())
        self.save_store()

    def remove_follower(self, username):
        self.store.followers.discard(username.lower())
        self.save_store()

    def get_rejected(self):
        return self.store.rejected

    def is_rejected(self, username):
        return username.lower() in self.store.rejected

    def add_rejected(self, username):
        self.store.rejected.add(username.lower())
        self.store.allowed.discard(username.lower())
        self.save_store()

    def remove_rejected(self, username):
        self.store.rejected.discard(username.lower())
        self.save_store()

    def get_allowed(self):
        return self.store.allowed

    def is_allowed(self, username):
        return username.lower() in self.store.allowed

    def add_allowed(self, username):
        self.store.allowed.add(username.lower())
        self.store.rejected.discard(username.lower())
        self.save_store()

    def remove_allowed(self, username):
        self.store.allowed.discard(username.lower())
        self.save_store()

    def remove_user(self, username):
        self.store.allowed.discard(username.lower())
        self.store.rejected.discard(username.lower())
        self.save_store()
