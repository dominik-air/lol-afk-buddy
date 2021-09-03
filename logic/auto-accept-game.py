#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import pyautogui
import time
import json
import os
import numpy as np
from mail import send_mail
from logic.image_manipulation import template_matching

# loading templates

# IP - image processing
PATH_IP = os.path.join(os.getcwd(), 'app', 'img', 'buttons_images')
PATH_LABELS = os.path.join(os.getcwd(), 'app', 'img', 'champion_select_images')

try:
    accept_button_img = cv2.imread(os.path.join(PATH_IP, 'accept.png'),
                                cv2.IMREAD_GRAYSCALE)
    ban_phase_indicator = cv2.imread(os.path.join(PATH_LABELS, 'ban a champion.png'),
                                    cv2.IMREAD_GRAYSCALE)
    ban_button_img = cv2.imread(os.path.join(PATH_IP, 'after ban select'),
                                cv2.IMREAD_GRAYSCALE)
    search_bar = cv2.imread(os.path.join(PATH_IP, 'search bar banning.png'),
                            cv2.IMREAD_GRAYSCALE)

    # GDZIE JEST PLIK champions_data.json?????????
    # no zgubił się, ale webscraper go ma ogarniać i ogólnie już to powinno działać
    with open("../data/champions.json", "r") as champions_file:
        champions = json.load(champions_file)
except Exception as e:
    print(e)


def queue_stage(screen):
    accept_button_loc = template_matching(template=accept_button_img, search_img=screen)
    if accept_button_loc is None:
        return False  # change to True for testing in customs
    else:
        top_left, bottom_right = accept_button_loc
        center_x = int((top_left[0] + bottom_right[0]) / 2)
        center_y = int((top_left[1] + bottom_right[1]) / 2)
        pyautogui.click(center_x, center_y)
        send_mail()
        return True


def banning_phase(screen):
    banning_phase_loc = template_matching(
        template=ban_phase_indicator, search_img=screen
    )
    if banning_phase_loc is None:
        return False
    else:
        search_bar_loc = template_matching(template=search_bar, search_img=screen)
        if search_bar_loc is None:
            return False
        else:
            top_left, bottom_right = search_bar_loc
            center_x = int((top_left[0] + bottom_right[0]) / 2)
            center_y = int((top_left[1] + bottom_right[1]) / 2)
            pyautogui.click(center_x, center_y)

            ban_target = "Teemo"
            pyautogui.write(ban_target)
            time.sleep(0.5)
            screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2GRAY)
            ban_target_img = cv2.imread(
                "champion_images/" + ban_target + ".png", cv2.IMREAD_GRAYSCALE
            )

            ban_target_loc = template_matching(
                template=ban_target_img, search_img=screen, threshold=0.70
            )

            if ban_target_loc is None:
                return False
            else:
                top_left, bottom_right = ban_target_loc
                center_x = int((top_left[0] + bottom_right[0]) / 2)
                center_y = int((top_left[1] + bottom_right[1]) / 2)
                pyautogui.click(center_x, center_y)

                screen = cv2.cvtColor(
                    np.array(pyautogui.screenshot()), cv2.COLOR_RGB2GRAY
                )

                ban_button_loc = template_matching(
                    template=ban_button_img, search_img=screen
                )

                if ban_button_loc is None:
                    return False
                else:
                    top_left, bottom_right = ban_button_loc
                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)
                    pyautogui.click(center_x, center_y)
                    return True


def picking_phase(screen):
    print("not implemented")
    return True


def ban_champion(target):
    raise NotImplementedError


while True:
    ans = pyautogui.confirm("MENU", buttons=["START", "USTAWIENIA", "WYJŚCIE"])

    if ans == "START":
        stages = (stage for stage in [queue_stage, banning_phase, picking_phase])
        stage = next(stages)
        while True:
            try:
                screen = cv2.cvtColor(
                    np.array(pyautogui.screenshot()), cv2.COLOR_RGB2GRAY
                )
                ret = stage(screen)
                if ret:
                    stage = next(stages)
            except StopIteration:
                break
    elif ans == "USTAWIENIA":
        ban_target = pyautogui.prompt(
            text="Jaką postać zbanować w champion select?",
            title="Ustawienie banowania",
            default="Teemo",
        )
        # work in progress
        if ban_target is not None and ban_target.lower() in champions:
            # ban_champion(target=ban_target)
            print("zbanowano", ban_target)
        else:
            print("nie ma takiego czempiona")

    elif ans == "WYJŚCIE":
        break
