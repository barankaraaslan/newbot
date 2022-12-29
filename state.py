#!/bin/env python
from multiprocessing import Lock, Pool
from os import makedirs
from pygetwindow import Window, getWindowsWithTitle
from PIL.ImageGrab import grab
from PIL import Image
from numpy import array, array_equal
import json
from dataclasses import dataclass
from pyautogui import click
from time import sleep
import logging
from glob import glob
from pathlib import Path
from functools import wraps

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class Point:
    x: int
    y: int

class Pos:
    def __init__(self, top_left_x, top_left_y, bottom_right_x, bottom_right_y) -> None:
        self.tl = Point(top_left_x, top_left_y)
        self.br = Point(bottom_right_x, bottom_right_y)
        self.dx = bottom_right_x - top_left_x
        self.dy = bottom_right_y - top_left_y

    def __repr__(self) -> str:
        return f'({self.tl.x},{self.tl.y},{self.br.x},{self.br.y})'

class Data(metaclass=Singleton):
    """Read position and action data through this class"""
    def __init__(self):
        with open("data/pos_data.json", "r") as pos_data_file:
            self.pos_data = json.load(pos_data_file)
        with open("data/action_data.json", "r") as action_data_file:
            self.action_data = json.load(action_data_file)


class Game(metaclass=Singleton):
    def __init__(self):
        self.window: Window = getWindowsWithTitle("Yu-Gi-Oh! DUEL LINKS")[0]
        self.window.activate()
        self.window.moveTo(0, 0)
        self.refresh_screen()

    def refresh_screen(self):
        self.screenshot = array(
            grab(
                bbox=(
                    int(self.window.left),
                    int(self.window.top),
                    int(self.window.left + self.window.width),
                    int(self.window.top + self.window.height),
                )
            )
        )

def log(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        logging.debug(f'calling {func.__name__} with params {args}, {kwargs}')
        result = func(*args, **kwargs)
        logging.debug(f'{func.__name__} returned {result}')
        return result
    return wrapped

def debug_save_image(array, name):
    makedirs('debug', exist_ok=True)
    Image.fromarray(array).save(f"debug/{name}.png")
    logging.debug(f'saving {name}.png')

def debug_image(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        for arg in *args, *kwargs.values():
            if type(arg) == SimpleState:
                debug_save_image(arg.image, arg.name)
        result = func(*args, **kwargs)
        return result
    return wrapped


class SimpleState:
    def __init__(self, name) -> None:
        self.name = name
        self.pos_data = Pos(*Data().pos_data[name].values())
        self.action_data = Data().action_data[name]
        self._image = None

    @property
    def image(self):
        if self._image is None:
            self._image = array(Image.open(f"data/simple_state/{self.name}.png"))
        return self._image
        
    def __bool__(self) -> bool:
        rhs = Game().screenshot[self.pos_data.tl.y : self.pos_data.br.y, self.pos_data.tl.x : self.pos_data.br.x]
        debug_save_image(rhs, 'rhs')
        return array_equal(self.image, rhs)

    def __call__(self):
        click(**self.action_data)
        sleep(5)

    def __repr__(self):
        return f'SimpleState({self.name})'

def get_simple_states():
    for image_path in glob('data/simple_state/*.png'):
        # Extract state name from the image file name and return a state object
        yield SimpleState(Path(image_path).name.removesuffix('.png'))

def state_checker_worker(states, action_lock: Lock):
    while True:
        for state in states:
            if state:
                action_lock.acquire()
                state()
                action_lock.release()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    states = list(get_simple_states())

    while True:
        for state in states:
            if state:
                logging.info(f'detected current state is {state.name}')
                state()
