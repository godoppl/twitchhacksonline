# "Twitch Hacks Online"
# 2020 - Frank Godo

import socket
import logging

logger = logging.getLogger(__name__)


class KbdClient():
    available = False

    def __init__(self, server):
        self.server = server
        logger.info("Initializing Keyboard passthrough on %s", server)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        try:
            self.s.connect(self.server)
            self.available = True
        except (OSError, TypeError):
            logger.error("Keyboard passthough is not available")

    def reconnect(self):
        if self.available:
            self.s.close()
        self.connect()

    def send_keys(self, keys):
        if not self.available:
            logger.info("Unable to send keys")
            return
        key_string = ",".join(keys)
        self.s.sendall(f"1{key_string}".encode())

    def send_command(self, command):
        if not self.available:
            logger.info("Unable to send commands")
            return
        self.s.sendall(f"2{command}".encode())
