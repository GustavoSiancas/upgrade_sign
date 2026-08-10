import cv2
import numpy as np


def upgrade_sign_v3(image_bytes: bytes, format: str = ".png") -> bytes:
    # 1. Leer imagen en memoria conservando el canal Alpha si ya existía
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    # CASO A: Si la imagen ya pasó por el filtro y es un PNG con Alpha (4 canales)
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        _, mask = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)

    # CASO B: Imagen normal para procesar extracción de color rojo
    else:
        # Asegurar formato BGR (3 canales)
        if len(img.shape) == 2:
            img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_bgr = img[:, :, :3]

        # Convertir a espacio de color HSV
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Rango 1: Tonos de rojo en el límite inferior
        lower_red1 = np.array([0, 40, 20])
        upper_red1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

        # Rango 2: Tonos de rojo en el límite superior
        lower_red2 = np.array([170, 40, 20])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        # Unir ambas máscaras rojas
        mask = cv2.bitwise_or(mask1, mask2)

        # Fallback: Si no hay rojo (por ejemplo, firma con tinta negra muy oscura o sombra dura),
        # usar la normalización de iluminación de tu v3 original
        if cv2.countNonZero(mask) == 0:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            background = cv2.GaussianBlur(gray, (31, 31), 0)
            normalized = cv2.divide(gray, background, scale=255)
            _, mask = cv2.threshold(
                normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

        # Operaciones morfológicas para limpiar ruido y unir trazados
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Crear imagen RGBA con firma negra transparente
    result = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
    result[:, :, 0] = 0  # B
    result[:, :, 1] = 0  # G
    result[:, :, 2] = 0  # R
    result[:, :, 3] = mask  # Alpha

    # Codificar a PNG en memoria
    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()