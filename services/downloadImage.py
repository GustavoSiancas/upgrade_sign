from io import BytesIO

import requests
from PIL import Image


class DownloadImageService:

    @staticmethod
    def download_as_png_bytes(
        image_url: str,
        timeout: int = 30
    ) -> bytes:

        response = requests.get(image_url, timeout=timeout)
        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as image:
            output = BytesIO()

            image.convert("RGBA").save(output, format="PNG")

            return output.getvalue()