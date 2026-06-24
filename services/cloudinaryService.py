from pathlib import Path
from urllib.parse import urlparse
import config.cloudinaryConfig

import requests
import cloudinary
import cloudinary.uploader


def download_image(image_url: str, download_folder: str = "uploads") -> str:
    Path(download_folder).mkdir(exist_ok=True)

    filename = Path(urlparse(image_url).path).name

    output_path = str(Path(download_folder) / filename)

    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path


def upload_image(file_path: str, folder: str = "signatures") -> str:
    filename = Path(file_path).stem

    result = cloudinary.uploader.upload(
        file_path,
        folder=folder,
        public_id=filename,
        overwrite=True,
        resource_type="image"
    )

    return result["secure_url"]