from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from carnet import carnetService
from pdf import pdfService

from sign.upgradeSign import upgrade_sign
from sign.upgradeSignv import upgrade_sign_v5
from services.imageService import resize_image, resize_signature
from services.cloudinaryService import (
    download_image,
    upload_image,
    upload_pdf
)

app = FastAPI(
    title="Upgrade Sign API",
    version="1.0.0"
)


class SignRequest(BaseModel):
    imageUrl: str

class ImageRequest(BaseModel):
    imageUrl: str

class CarnetRequest(BaseModel):
    imageUrl: str
    signatureUrl: str
    dni: str
    names: str
    lastNames: str
    nro_registro: str
    url: str

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

    resized= resize_image(
        processed_file,
        425,
        282
    )

    processed_url = upload_image(
        resized,
        folder="processed-signatures"
    )

    return {
        "processedUrl": processed_url
    }

@app.post("/resize-signature")
def resize_signature(request: ImageRequest):
    downloaded_file = download_image(
        request.imageUrl
    )

    path = Path(downloaded_file)

    resized = resize_image(
        path,
        425, 
        282
    )

    resized_url = upload_image(
        resized,
        folder="resized-images"
    )

    return {
        "resizedUrl": resized_url
    }

@app.post("/resize-photo")
def resize_photo(request: ImageRequest):
    downloaded_file = download_image(
        request.imageUrl
    )

    path = Path(downloaded_file)

    resized = resize_image(
        path,
        532,
        709
    )

    resized_url = upload_image(
        resized,
        folder="resized-photos"
    )

    return {
        "resizedUrl": resized_url
    }

@app.post("/carnet")
def generate_carnet(request: CarnetRequest):
    downloaded_photo = download_image(
        request.imageUrl
    )

    downloaded_signature = download_image(
        request.signatureUrl
    )

    carnet_service = carnetService.CarnetService()

    generated_carnet_path = carnet_service.generate(
        dni=request.dni,
        nombres=request.names,
        apellidos=request.lastNames,
        nro_registro=request.nro_registro,
        firma_path=downloaded_signature,
        image_path=downloaded_photo
    )

    generated_back_carnet_path = carnet_service.generate_back_carnet(
        dni=request.dni,
        url_qr=request.url,
        output_folder="output"
    )

    generated_pdf_path = pdfService.PdfService.generate_pdf(
        front_image_path=generated_carnet_path,
        back_image_path=generated_back_carnet_path,
        output_folder="output",
        filename=f"{request.dni}.pdf"
    )

    generated_carnet_url = upload_image(
        generated_carnet_path,
        folder="generated-carnets"
    )

    generated_back_carnet_url = upload_image(
        generated_back_carnet_path,
        folder="generated-back-carnets"
    )

    generated_pdf_url = upload_pdf(
        generated_pdf_path,
        folder="generated-pdfs"
    )

    return {
        "carnetUrl": generated_carnet_url,
        "backCarnetUrl": generated_back_carnet_url,
        "pdfUrl": generated_pdf_url
    }