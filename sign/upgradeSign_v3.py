import cv2
import numpy as np


def upgrade_sign_v3(image_bytes: bytes, format: str = ".png") -> bytes:
    # Leer imagen desde memoria
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Reducir ruido
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Normalizar iluminación para eliminar sombras
    background = cv2.GaussianBlur(gray, (31, 31), 0)
    normalized = cv2.divide(gray, background, scale=255)

    # Umbral automático
    _, mask = cv2.threshold(
        normalized,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Limpiar ruido pequeño
    kernel = np.ones((2, 2), np.uint8)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Unir pequeños cortes en la firma
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Crear imagen RGBA
    result = np.zeros(
        (mask.shape[0], mask.shape[1], 4),
        dtype=np.uint8
    )

    # Firma negra
    result[:, :, 0] = 0  # B
    result[:, :, 1] = 0  # G
    result[:, :, 2] = 0  # R

    # Canal alfa
    result[:, :, 3] = mask

    # Codificar a PNG en memoria
    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()