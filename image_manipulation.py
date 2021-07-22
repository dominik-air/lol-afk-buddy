#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple

Image = np.ndarray
Point = Tuple[int, int]
DiagonalCorners = Tuple[Point, Point]


class Cropper:
    """
    Useful for working with smaller regions of a bigger image. Combined with the template_matching function it
    should reduce the number of false positives by working on more specific areas of a given screen.

    Args:
        image: grayscale image the Cropper will work on.
    """
    def __init__(self, image: Image):
        self.__original_image = image
        self.__cropped_image = None
        self.__top_left_corner = None

    @property
    def original_image(self):
        return self.__original_image

    @property
    def cropped_image(self):
        return self.__cropped_image

    def crop(self, top_left_corner: Point, bottom_right_corner: Point) -> None:
        """
        Crops the original image to a rectangular image which dimensions are restricted by the top left and bottom
        right corners. The cropped image and the top left corner are saved in class fields.

        Args:
            top_left_corner: pair of (x, y) coordinates of the top left corner of a rectangle.
            bottom_right_corner: pair of (x, y) coordinates of the bottom right corner of a rectangle.
        """
        self.__top_left_corner = top_left_corner
        x_top_left, y_top_left = top_left_corner
        x_bottom_right, y_bottom_right = bottom_right_corner
        self.__cropped_image = self.original_image[y_top_left:y_bottom_right, x_top_left:x_bottom_right]

    def cropped_image_coords_to_original_image_coords(self, x_cropped: int, y_cropped: int) -> Point:
        """
        Transforms cropped image coordinates back to the original image coordinates by adding the cropping offsets,
        that is the top left corner coordinates, to the cropped image coordinates.

        Args:
            x_cropped: x coordinate of an object in the cropped image
            y_cropped: y coordinate of an object in the cropped image

        Returns:
            The coordinates in the original image coordinates set.
        """
        return x_cropped + self.__top_left_corner[0], y_cropped + self.__top_left_corner[1]


def template_matching(template: Image, search_img: Image, threshold: float = 0.80) -> Optional[DiagonalCorners]:
    """
    Function searches and finds the location of a template image in a larger search image and returns the diagonal
    corners of the best fit rectangle that exceeds a given threshold.

    Args:
        template: image that is searched for in the search image.
        search_img: image that the template image is searched in.
        threshold: real number between 0 and 1 determining how fussy the template matching algorithm should be.

    Returns:
        Tuple of the top left corner and the bottom right corner of the rectangle that surrounds the best fit.
        If the best fit value is below the provided threshold then the function returns None.
    """
    height, width = template.shape
    img = search_img.copy()
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        top_left_corner = max_loc
        bottom_right_corner = (top_left_corner[0] + width, top_left_corner[1] + height)
        return top_left_corner, bottom_right_corner
    else:
        return None


if __name__ == "__main__":
    # loads templates
    accept_button_img = cv2.imread('data/accept.png', cv2.IMREAD_GRAYSCALE)
    decline_button_img = cv2.imread('data/decline.png', cv2.IMREAD_GRAYSCALE)

    # loads the image of search and makes a grayscale copy for template matching
    test_screen = cv2.cvtColor(cv2.imread('data/test_screen.png'), cv2.COLOR_BGR2RGB)
    gray_test_screen = cv2.cvtColor(test_screen, cv2.COLOR_RGB2GRAY)

    top_left_accept, bottom_right_accept = template_matching(template=accept_button_img, search_img=gray_test_screen)
    top_left_decline, bottom_right_decline = template_matching(template=decline_button_img, search_img=gray_test_screen)

    # draws rectangles around detected templates
    cv2.rectangle(test_screen, top_left_accept, bottom_right_accept, color=(0, 255, 0), thickness=2)
    cv2.rectangle(test_screen, top_left_decline, bottom_right_decline, color=(255, 0, 0), thickness=2)

    # plots the results
    plt.figure(figsize=(16, 9))
    plt.imshow(test_screen)
    plt.xticks([], [])
    plt.yticks([], [])
    plt.title('Template matching test', fontsize=20)
    plt.show()
