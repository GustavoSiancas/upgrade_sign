import cv2
import numpy as np

def upgrade_sign_v2(image_bytes: bytes, format: str = ".png") -> bytes:
    # 1. Leer imagen conservando transparencia si ya la tiene
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    # CASO A: La imagen ya es un PNG transparente de 4 canales (vueltas subsiguientes)
    if len(img.shape) == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        _, mask = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)

    # CASO B: Es una imagen estándar de 1 o 3 canales
    else:
        # Asegurar BGR de 3 canales para HSV
        if len(img.shape) == 2:
            img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_bgr = img[:, :, :3]

        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Filtro para detectar tinta AZUL
        lower_blue = np.array([90, 40, 20])
        upper_blue = np.array([150, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # SI NO ENCONTRÓ AZUL (ej. la firma es negra o la máscara quedó vacía):
        if cv2.countNonZero(mask) == 0:
            # Fallback: Umbralización estándar sobre escala de grises
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            _, mask = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

        # Limpieza morfológica de ruido
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Construir imagen resultante (Firma en negro puro con canal Alpha)
    result = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
    result[:, :, 0] = 0  # B
    result[:, :, 1] = 0  # G
    result[:, :, 2] = 0  # R
    result[:, :, 3] = mask  # Alpha

    # Codificar en memoria
    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()