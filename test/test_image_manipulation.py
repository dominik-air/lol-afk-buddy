import unittest
import cv2
import numpy as np
from image_manipulation import Cropper


class CropperTest(unittest.TestCase):
    def setUp(self):
        self.test_image = cv2.imread("../data/test_screen.png", cv2.IMREAD_GRAYSCALE)
        self.test_cropper = Cropper(image=self.test_image)
        self.top_left_crop_corner = (900, 430)
        self.bottom_left_crop_corner = (900 + 110, 430 + 110)

    def test_crop(self):
        result_image = cv2.imread("../data/crop_test_result.png", cv2.IMREAD_GRAYSCALE)

        self.test_cropper.crop(top_left_corner=self.top_left_crop_corner,
                               bottom_right_corner=self.bottom_left_crop_corner)
        self.assertTrue(np.all(self.test_cropper.cropped_image == result_image))

    def test_cropped_image_coords_to_original_image_coords(self):
        x, y = self.top_left_crop_corner
        original_coords = (x + 20, y + 30)

        self.test_cropper.crop(top_left_corner=self.top_left_crop_corner,
                               bottom_right_corner=self.bottom_left_crop_corner)
        transformed_coords = self.test_cropper.cropped_image_coords_to_original_image_coords(x_cropped=20, y_cropped=30)
        self.assertTupleEqual(original_coords, transformed_coords)


if __name__ == '__main__':
    unittest.main()
