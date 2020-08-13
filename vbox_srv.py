# twitchhacks.online
# "Twitch Hacks Online"
# 2020 - Frank Godo

import time
import logging
import virtualbox
from virtualbox.library import VBoxErrorObjectNotFound
from settings import MACHINE_NAME

logger = logging.getLogger(__name__)

KEYBOARD_KEYS = ['ESC', '1', '!', '2', '@', '3', '#', '4', '$', '5', '%', '6', '^', '7', '&', '8', '*',
                 '9', '(', '0', ')', '-', '_', '=', '+', 'BKSP', '\x08', 'TAB', '\t', 'q', 'Q', 'w', 'W',
                 'e', 'E', 'r', 'R', 't', 'T', 'y', 'Y', 'u', 'U', 'i', 'I', 'o', 'O', 'p', 'P', '[', '{',
                 ']', '}', 'ENTER', '\r', '\n', 'CTRL', 'a', 'A', 's', 'S', 'd', 'D', 'f', 'F', 'g', 'G',
                 'h', 'H', 'j', 'J', 'k', 'K', 'l', 'L', ';', ':', "'", '"', '`', '~', 'LSHIFT', '\\', '|',
                 'z', 'Z', 'x', 'X', 'c', 'C', 'v', 'V', 'b', 'B', 'n', 'N', 'm', 'M', ',', '<', '.', '>',
                 '/', '?', 'RSHIFT', 'PRTSC', 'ALT', 'SPACE', ' ', 'CAPS', 'F1', 'F2', 'F3', 'F4', 'F5',
                 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'NUM', 'SCRL', 'HOME', 'UP', 'PGUP', 'MINUS',
                 'LEFT', 'CENTER', 'RIGHT', 'PLUS', 'END', 'DOWN', 'PGDN', 'INS', 'DEL', 'E_DIV', 'E_ENTER',
                 'E_INS', 'E_DEL', 'E_HOME', 'E_END', 'E_PGUP', 'E_PGDN', 'E_LEFT', 'E_RIGHT', 'E_UP',
                 'E_DOWN', 'RALT', 'RCTRL', 'LWIN', 'RWIN', 'PAUSE']
MODIFIERS = ['CTRL', 'SHIFT', 'LSHIFT', 'RSHIFT', 'ALT', 'RALT', 'RCTRL', 'LWIN', 'RWIN', 'WIN']


class VirtualBoxSrv():
    def __init__(self):
        self.vbox = virtualbox.VirtualBox()
        self.session = virtualbox.Session()
        try:
            self.machine = self.vbox.find_machine(MACHINE_NAME)
            self.launch()
        except VBoxErrorObjectNotFound:
            logger.error('Could not locate VM %s', MACHINE_NAME)
            self.machine = None

    def launch(self):
        if not self.is_running() and self.machine:
            progress = self.machine.launch_vm_process(self.session, "gui", "")
            progress.wait_for_completion()

    def shut_down(self, save=False, restore=False):
        if self.is_running():
            if save:
                progress = self.session.machine.save_state()
            else:
                progress = self.session.console.power_down()
            progress.wait_for_completion()
        if restore:
            snapshot = self.session.machine.current_snapshot
            progress = self.session.machine.restore_snapshot(snapshot)
            progress.wait_for_completion()

    def snapshot(self, username):
        progress, _ = self.session.machine.take_snapshot(f"{int(time.time())}", f"Taken by {username}", True)
        progress.wait_for_completion()

    def is_running(self):
        if self.machine is None:
            return False
        return int(self.machine.state) == 5

    def type(self, text):
        if not self.is_running():
            return False
        if type(text) is not str:
            raise TypeError
        # Handle weird chars
        text = text.replace('€', '')
        text = text.replace('¡', '')
        self.session.console.keyboard.put_keys(text)

    def send(self, *args):
        if not self.is_running():
            return
        to_press = []
        to_hold = []
        for key in args:
            if len(key) > 1:
                key = key.upper()
            if key in MODIFIERS:
                if key in ['WIN', 'SHIFT']:
                    key = 'L' + key
                to_hold.append(key)
            elif key in KEYBOARD_KEYS:
                to_press.append(key)
            else:
                pass
        self.session.console.keyboard.put_keys(press_keys=to_press, hold_keys=to_hold)
        return ' '.join(to_hold + to_press)

    def release(self):
        if not self.is_running():
            return False
        self.session.console.keyboard.release_keys()
        return True
