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
    path = Path(file_path)

    try:
        result = cloudinary.uploader.upload(
            str(path),
            folder=folder,
            public_id=path.stem,
            overwrite=True,
            resource_type="image"
        )
        return result["secure_url"]
    finally:
        if path.exists():
            path.unlink()


def upload_pdf(
    file_path: str,
    folder: str = "pdfs"
) -> str:

    path = Path(file_path)

    try:
        result = cloudinary.uploader.upload(
            str(path),
            folder=folder,
            public_id=path.stem,
            overwrite=True,
            resource_type="raw"
        )

        return result["secure_url"]

    finally:
        if path.exists():
            path.unlink()