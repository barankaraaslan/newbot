#!/bin/env python
import json
from os import makedirs
from pathlib import Path
from sys import argv
from threading import Lock

import mouse
from PIL import ImageGrab
from pyautogui import position, click
from pygetwindow import Window, getWindowsWithTitle
from time import sleep
import keyboard
import functools

game_window: Window = getWindowsWithTitle("Yu-Gi-Oh! DUEL LINKS")[0]
game_window.activate()
game_window.moveTo(0,0)
def print_onclick(lock, button, event):
    pos = position()
    makedirs("data", exist_ok=True)
    action_data_path = Path("data/action_data.json")
    if not action_data_path.is_file():
        action_data_path.touch()
        with open(action_data_path, "w") as action_data_file:
            json.dump({}, action_data_file)

    with open(action_data_path, "r") as action_data_file:
        action_data = json.load(action_data_file)

    action_data[argv[1]] = {
        "x": pos.x - game_window.topleft.x,
        "y": pos.y - game_window.topleft.y,
        "button": button
    }
    with open(action_data_path, "w") as action_data_file:
        json.dump(action_data, action_data_file)
    lock.release()

lock = Lock()
lock.acquire()
left = functools.partial(print_onclick, lock, "LEFT")
right = functools.partial(print_onclick, lock, "RIGHT")
keyboard.on_press_key('a', left)
keyboard.on_press_key('d', right)
lock.acquire()