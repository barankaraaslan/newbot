#!/bin/env python 
import json
from time import sleep

import numpy as np
from PIL import Image
from PIL.ImageGrab import grab
from pyautogui import click
from pygetwindow import Window, getWindowsWithTitle

game_window: Window = getWindowsWithTitle("Yu-Gi-Oh! DUEL LINKS")[0]
game_window.activate()
game_window.moveTo(0, 0)
image_cache = {}
with open("data/pos_data.json", "r") as pos_data_file:
    pos_data = json.load(pos_data_file)
with open("data/action_data.json", "r") as action_data_file:
    action_data = json.load(action_data_file)


def open_image(image_name):
    if image_name in image_cache:
        return image_cache[image_name]
    image = Image.open(f"data/{image_name}.png")
    image_array = np.array(image)
    image_cache[image_name] = image_array
    return image_array


def is_state(state_name):
    image_array = open_image(state_name)
    pos_to_check = pos_data[state_name]
    current_screen = grab(
        bbox=(
            int(game_window.left + pos_to_check["top_left_x"]),
            int(game_window.top + pos_to_check["top_left_y"]),
            int(game_window.left + pos_to_check["bottom_right_x"]),
            int(game_window.top + pos_to_check["bottom_right_y"]),
        )
    )
    current_screen = np.array(current_screen)
    return np.array_equal(image_array, current_screen)

def cont(name, delay=7):
    print(f'found {name}')
    click(**action_data[f"SKIP_{name}"])
    sleep(delay)

def action(state_name):
    cont(state_name)

while True:
    for state_name in pos_data:
        if is_state(state_name):
            action(state_name)
    print("nothing to do... sleeping...")
    sleep(1) 
