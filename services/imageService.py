from io import BytesIO
from PIL import Image, ImageOps


def resize_signature(
    image_bytes: bytes,
    width: int,
    height: int
) -> bytes:

    image = Image.open(BytesIO(image_bytes)).convert("RGBA")

    original_width, original_height = image.size

    scale = max(
        width / original_width,
        height / original_height
    )

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    left = (new_width - width) // 2
    top = (new_height - height) // 2
    right = left + width
    bottom = top + height

    image = image.crop(
        (left, top, right, bottom)
    )

    output = BytesIO()
    image.save(output, format="PNG")

    return output.getvalue()


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