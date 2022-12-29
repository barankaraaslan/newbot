#!/bin/env python
import json
from os import makedirs
from pathlib import Path
from sys import argv
from time import sleep
import mouse
from PIL import ImageGrab
from pyautogui import position
from pygetwindow import Window, getWindowsWithTitle
import keyboard

game_window: Window = getWindowsWithTitle("Yu-Gi-Oh! DUEL LINKS")[0]
game_window.activate()
game_window.moveTo(0,0)

keyboard.wait('space')
top_left_pos = position()
keyboard.wait('space')
bottom_right_pos = position()

makedirs("data", exist_ok=True)
img = ImageGrab.grab(
    bbox=(
        int(top_left_pos.x),
        int(top_left_pos.y),
        int(bottom_right_pos.x),
        int(bottom_right_pos.y),
    )
)

pos_data_path = Path("data/pos_data.json")
if not pos_data_path.is_file():
    pos_data_path.touch()
    with open(pos_data_path, "w") as pos_data_file:
        json.dump({}, pos_data_file)

with open(pos_data_path, "r") as pos_data_file:
    pos_data = json.load(pos_data_file)

pos_data[argv[1]] = {
    "top_left_x": top_left_pos.x - game_window.topleft.x,
    "top_left_y": top_left_pos.y - game_window.topleft.y,
    "bottom_right_x": bottom_right_pos.x - game_window.topleft.x,
    "bottom_right_y": bottom_right_pos.y - game_window.topleft.y,
}
with open(pos_data_path, "w") as pos_data_file:
    json.dump(pos_data, pos_data_file)

img.save(f"data/{argv[1]}.png")
