import cv2
import numpy as np

def upgrade_sign_v1(image_bytes: bytes, format: str = ".png") -> bytes:
    # Leer imagen desde memoria conservando el canal Alpha si existe
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError("No se pudo leer la imagen.")

    # 1. Verificar si la imagen tiene 3 dimensiones (alto, ancho, canales)
    # y si efectivamente tiene 4 canales (RGBA / BGRA)
    if len(img.shape) == 3 and img.shape[2] == 4:
        # Extraer canal Alpha
        alpha = img[:, :, 3]
        
        # Limpiar canal alpha por si tiene residuos
        _, thresh = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
        
        result = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
        result[:, :, 3] = thresh  # B=0, G=0, R=0 (negro), Alpha=thresh

    # 2. Si es imagen en escala de grises (2D) o de 3 canales (RGB/BGR)
    else:
        # Si tiene 3 canales BGR, convertir a escala de grises
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
        else:
            # Ya era una imagen 2D en escala de grises
            gray = img

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

        result = np.zeros((thresh.shape[0], thresh.shape[1], 4), dtype=np.uint8)
        result[:, :, 3] = thresh  # B=0, G=0, R=0 (negro), Alpha=thresh

    # Codificar en memoria
    success, buffer = cv2.imencode(format, result)

    if not success:
        raise RuntimeError("No se pudo codificar la imagen.")

    return buffer.tobytes()