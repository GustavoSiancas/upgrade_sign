from io import BytesIO
from PIL import Image, ImageOps


def resize_signature(
    image_bytes: bytes,
    width: int,
    height: int,
    padding: int = 25
) -> dict[str, bytes]:
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    # Obtener el canal alfa para localizar el contenido visible.
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()

    if bbox is None:
        raise ValueError("La imagen no contiene una firma visible.")

    # Recortar todo el espacio transparente.
    signature = image.crop(bbox)

    available_width = width - (padding * 2)
    available_height = height - (padding * 2)

    if available_width <= 0 or available_height <= 0:
        raise ValueError(
            "El padding es demasiado grande para las dimensiones solicitadas."
        )

    signature_width, signature_height = signature.size

    # Mantener proporción usando al máximo el área disponible.
    scale = min(
        available_width / signature_width,
        available_height / signature_height
    )

    new_width = max(1, round(signature_width * scale))
    new_height = max(1, round(signature_height * scale))

    signature = signature.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    # Crear el lienzo final transparente.
    canvas = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    # Centrar la firma.
    x = (width - new_width) // 2
    y = (height - new_height) // 2

    canvas.alpha_composite(signature, (x, y))

    transparent_output = BytesIO()
    canvas.save(transparent_output, format="PNG")

    # Componer la misma firma sobre blanco sin perder el resultado transparente.
    white_canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    white_canvas.alpha_composite(canvas)

    white_output = BytesIO()
    white_canvas.convert("RGB").save(white_output, format="PNG")

    return {
        "transparent": transparent_output.getvalue(),
        "white": white_output.getvalue()
    }


def resize_image(
    image_bytes: bytes,
    width: int,
    height: int
) -> bytes:

    image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    image = ImageOps.fit(
        image,
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )

    output = BytesIO()
    image.save(output, format="PNG")

    return output.getvalue()
