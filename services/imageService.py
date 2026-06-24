from pathlib import Path
from PIL import Image


def resize_signature(
    input_path: str,
    width: int,
    height: int,
    output_folder: str = "processed"
) -> str:

    Path(output_folder).mkdir(exist_ok=True)

    image = Image.open(input_path).convert("RGBA")

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

    filename = Path(input_path).stem

    output_path = str(
        Path(output_folder) /
        f"{filename}_{width}x{height}.png"
    )

    image.save(output_path)

    return output_path