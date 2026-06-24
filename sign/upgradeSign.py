import cv2
import numpy as np


def upgrade_sign(input_path: str, output_path: str) -> str:
    img = cv2.imread(input_path)

    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {input_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    kernel = np.ones((2, 2), np.uint8)

    thresh = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        kernel
    )

    result = np.zeros(
        (thresh.shape[0], thresh.shape[1], 4),
        dtype=np.uint8
    )

    result[:, :, 0] = 0
    result[:, :, 1] = 0
    result[:, :, 2] = 0
    result[:, :, 3] = thresh

    cv2.imwrite(output_path, result)

    return output_path