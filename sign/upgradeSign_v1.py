import cv2
import numpy as np

def upgrade_sign_v1(image_bytes: bytes, format: str = ".png") -> bytes:
    # Leer imagen desde memoria conservando el canal Alpha si ya lo tiene
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    # CASO 1: La imagen ya tiene 4 canales (RGBA / BGRA) porque pasó por el filtro antes
    if img.shape[2] == 4:
        # Separar canales
        b, g, r, alpha = cv2.split(img)
        
        # Opcional: limpiar un poco el canal alpha por si quedaron residuos grises
        _, thresh = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
        
        # Reconstruir asegurando que sea negro puro con su transparencia limpia
        result = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
        result[:, :, 0] = 0  # B
        result[:, :, 1] = 0  # G
        result[:, :, 2] = 0  # R
        result[:, :, 3] = thresh  # Alpha original limpio

    # CASO 2: Es una imagen normal de 3 canales (RGB / BGR) por primera vez
    else:
        # Si tiene 3 canales, descartamos el canal extra si viniera en formato extraño
        img_bgr = img[:, :, :3]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
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

        # Negro con transparencia
        result[:, :, 0] = 0
        result[:, :, 1] = 0
        result[:, :, 2] = 0
        result[:, :, 3] = thresh

    # Codificar en memoria
    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()