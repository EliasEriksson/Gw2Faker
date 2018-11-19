from typing import Union
from itertools import chain
from time import sleep
import base64 as b64
import random
import json
import re
from pynput.keyboard import Key, Controller, KeyCode
from pynput import keyboard as keybrd
import pyperclip


class Faker:
    def __init__(self):
        with open("settings.json") as f:
            settings = json.load(f)

        self.links = self.load_gamelinks(settings["kp"])

        key_map = {"shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt, "lctrl": Key.ctrl_l,
                   "rctrl": Key.ctrl_r, "lshift": Key.shift_l, "rshift": Key.shift_r,
                   "alt gr": Key.alt_gr, "altgr": Key.alt_gr}

        self.keybind = set()
        for key in settings["keybind"]:
            if key in key_map:
                self.keybind.add(key_map[key])
            else:
                self.keybind.add(KeyCode.from_char(key))

        self.max_spam = settings["spam_settings"]["max_spam"]
        self.min_spam = settings["spam_settings"]["min_spam"]
        self.current_held_keys = set()

    def load_gamelinks(self, game_links: dict) -> dict:
        """
        decodes the given links and replaces the ammount with an 'x'

        once decoded, replace the x with with a number 0 <= x < 256
        and encode again for a edited link
        :param game_links: dict
        :return: dict
        """

        links = {}
        for encounter, game_link in game_links.items():
            decimal_string = self.from_game_link_to_decimal(game_link)
            match = re.search(r"(\d\s)\d+(\s\d+\s\d+\s\d+\s\d+)", decimal_string)
            if match.groups():
                groups = match.groups()
                links.update({encounter: "".join(chain(groups[0], "x", groups[1]))})
        return links

    @staticmethod
    def from_decimal_to_game_link(decimal_string: str) -> str:
        """
        encodes a gw2 chat link from a decimal string

        legendary insight ingame link "[&AgH2LQEA]"
        legendary insight decoded ingame link "2 1 246 45 1 0"

        :param decimal_string: str, decimal string
        :return: str, ingame link
        """
        decimal_string = decimal_string.split(" ")
        decimal_string = bytes([int(c) for c in decimal_string])
        b64_string = b64.b64encode(decimal_string)
        new_game_link = "[&" + "".join([chr(c) for c in b64_string]) + "]"
        return new_game_link

    @staticmethod
    def from_game_link_to_decimal(game_link: str) -> str:
        """
        decodes a gw2 link to decimal form

        :param game_link: str
        :return: str
        """
        game_link = game_link.strip("[")
        game_link = game_link.strip("]")
        game_link = game_link.strip("&")
        return " ".join([str(c) for c in b64.b64decode(game_link)])

    @staticmethod
    def timer() -> None:
        """
        extra time so so messages are sent at random intervals to anets servers

        :return: None
        """
        sleep(random.randint(10, 30) / 1000)

    def process_links(self, links: list) -> None:
        """
        spams the prepared game links

        links passed on from self.process_arguments
        :param links: list
        :return: None
        """
        keyboard = Controller()

        for _ in range(random.randint(self.min_spam, self.max_spam)):
            for link in links:
                pyperclip.copy(link)
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                self.timer()
                with keyboard.pressed(Key.ctrl_l):
                    self.timer()
                    keyboard.press("v")
                    keyboard.release("v")
                    self.timer()
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                self.timer()

    def process_arguments(self, args: list) -> list:
        """
        preparing game links to spam

        adds the ammount of of each kp to be spammed
        arguments passed on from self.process_clipboard()
        :param args: list
        :return: list
        """
        return [self.from_decimal_to_game_link(self.links[kp].replace("x", ammount))
                for ammount, kp in args]

    @staticmethod
    def process_clipboard(clipboard: str) -> list:
        """
        checks if the clipboard is a /faker command and contains valid arguments

        :param clipboard: str
        :return: list
        """
        sub = re.search(r"^/faker\s(.)*$", clipboard)
        if sub:
            sub = sub.string.strip("/faker")

            args = re.findall(r"\s(\d+\s\w*)", sub)
            if args:
                return args

            args = re.findall(r"\s(\d+)(\w+)", sub)
            if args:
                return args

    def on_press(self, key: Union[Key, KeyCode]):
        """
        start to spam if clipboard contains valid arguments and keybinding isheld down

        also updates the keys for the keybindings
        :param key: Union[Key, KeyCode]
        :return: None
        """
        if key in self.keybind:
            self.current_held_keys.add(key)
            if all(k in self.current_held_keys for k in self.keybind):
                clipboard = pyperclip.paste()
                args = self.process_clipboard(clipboard)
                if args:
                    links = self.process_arguments(args)
                    if links:
                        self.process_links(links)
                pyperclip.copy(clipboard)

    def on_release(self, key: Union[Key, KeyCode]) -> None:
        """
        updates the set of keys for the keybinding that are held down

        :param key: Union[Key, KeyCode]
        :return: None
        """
        try:
            self.current_held_keys.remove(key)
        except KeyError:
            pass

    def run(self) -> None:
        """
        call on an instance of Faker to run the program

        :return: None
        """
        with keybrd.Listener(self.on_press, self.on_release) as listener:
            listener.join()


if __name__ == '__main__':
    Faker().run()
    # /faker 50li 60vg
    """    
    """