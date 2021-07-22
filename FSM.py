import time
import pyautogui
from image_manipulation import Cropper, template_matching


class State:
    def __init__(self):
        raise NotImplementedError


class StateMachine:
    def __init__(self):
        raise NotImplementedError

