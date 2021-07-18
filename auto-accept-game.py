#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import pyautogui
import time
import json
import numpy as np
from mail import send_mail
from match import template_matching

# loading templates
accept_button_img = cv2.imread('data/accept.png', cv2.IMREAD_GRAYSCALE)

with open("data/champions.json", "r") as champions_file:
    bannable_champions = json.load(champions_file)


def ban_champion(target):
    raise NotImplementedError


while True:
    ans = pyautogui.confirm('MENU', buttons=['START', 'USTAWIENIA', 'WYJŚCIE'])

    if ans == 'START':
        while True:
            screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2GRAY)
            try:
                top_left, bottom_right = template_matching(template=accept_button_img, search_img=screen)
                center_x = int((top_left[0] + bottom_right[0]) / 2)
                center_y = int((top_left[1] + bottom_right[1]) / 2)
                pyautogui.click(center_x, center_y)
                send_mail()
                break
            except ValueError:
                time.sleep(1)

    elif ans == "USTAWIENIA":
        ban_target = pyautogui.prompt(text='Jaką postać zbanować w champion select?', title='Ustawienie banowania',
                                      default='Teemo')
        # work in progress
        if ban_target is not None and ban_target.lower() in bannable_champions:
            #ban_champion(target=ban_target)
            print('zbanowano', ban_target)
        else:
            print('nie ma takiego czempiona')

    elif ans == "WYJŚCIE":
        break
