import cv2
import numpy as np


def upgrade_sign_v2(image_bytes: bytes, format: str = ".png") -> bytes:
    # Convertir bytes a imagen
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([90, 40, 20])
    upper_blue = np.array([150, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

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

    # Negro con transparencia
    result[:, :, 0] = 0
    result[:, :, 1] = 0
    result[:, :, 2] = 0
    result[:, :, 3] = mask

    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()