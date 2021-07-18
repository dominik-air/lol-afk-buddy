#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import matplotlib.pyplot as plt


def template_matching(template, search_img):
    width, height = template.shape[::-1]
    img = search_img.copy()
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= 0.80:
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        return top_left, bottom_right
    else:
        raise ValueError('Nothing interesting was found!')


if __name__ == "__main__":
    # loading templates
    accept_button_img = cv2.imread('accept.png', cv2.IMREAD_GRAYSCALE)
    decline_button_img = cv2.imread('decline.png', cv2.IMREAD_GRAYSCALE)

    # loading the image of search
    test_screen_img = cv2.cvtColor(cv2.imread('test_screen.png'), cv2.COLOR_BGR2RGB)
    gray_test_screen_img = cv2.cvtColor(test_screen_img, cv2.COLOR_RGB2GRAY)

    top_left_accept, bottom_right_accept = template_matching(template=accept_button_img, search_img=gray_test_screen_img)
    top_left_decline, bottom_right_decline = template_matching(template=decline_button_img, search_img=gray_test_screen_img)

    cv2.rectangle(test_screen_img, top_left_accept, bottom_right_accept, (0, 255, 0), 2)
    cv2.rectangle(test_screen_img, top_left_decline, bottom_right_decline, (255, 0, 0), 2)

    plt.figure(figsize=(16, 9))
    plt.imshow(test_screen_img)
    plt.xticks([], [])
    plt.yticks([], [])
    plt.show()
