from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path

from sign.upgradeSign import upgrade_sign
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

    upgrade_sign(
        downloaded_file,
        processed_file
    )

    processed_url = upload_image(
        processed_file,
        folder="processed-signatures"
    )

    return {
        "processedUrl": processed_url
    }