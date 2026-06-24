from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path


from sign.upgradeSign import upgrade_sign
from sign.upgradeSignv import upgrade_sign_v5
from services.imageService import resize_signature
from services.cloudinaryService import (
    download_image,
    upload_image
)

app = FastAPI(
    title="Upgrade Sign API",
    version="1.0.0"
)


class SignRequest(BaseModel):
    imageUrl: str

class ImageRequest(BaseModel):
    imageUrl: str

@app.post("/upgrade-sign")
def upgrade_signature(request: SignRequest):

    downloaded_file = download_image(
        request.imageUrl
    )

    filename = Path(downloaded_file).name

    processed_file = str(
        Path("processed") / f"{filename}.png"
    )

    Path("processed").mkdir(exist_ok=True)

    upgrade_sign_v5(
        downloaded_file,
        processed_file
    )

    resized = resize_signature(
        processed_file,
        350,
        250
    )

    processed_url = upload_image(
        resized,
        folder="processed-signatures"
    )

    return {
        "processedUrl": processed_url
    }

@app.post("/resize-image")
def resize_image(request: ImageRequest):
    downloaded_file = download_image(
        request.imageUrl
    )

    path = Path(downloaded_file)

    resized = resize_signature(
        path,
        500,
        500
    )

    resized_url = upload_image(
        resized,
        folder="resized-images"
    )

    return {
        "resizedUrl": resized_url
    }