import cv2
import numpy as np


def upgrade_sign_v5(input_path: str, output_path: str):

    img = cv2.imread(input_path)

    hsv = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2HSV
    )

    lower_blue = np.array([90, 40, 20])
    upper_blue = np.array([150, 255, 255])

    mask = cv2.inRange(
        hsv,
        lower_blue,
        upper_blue
    )

    kernel = np.ones((2, 2), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    result = np.zeros(
        (mask.shape[0], mask.shape[1], 4),
        dtype=np.uint8
    )

    result[:, :, 0] = 0
    result[:, :, 1] = 0
    result[:, :, 2] = 0
    result[:, :, 3] = mask

    cv2.imwrite(output_path, result)

    return output_path