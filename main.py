from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from carnet import carnetService
from pdf import pdfService
from enum import Enum

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

class DocumentType(str, Enum):
    DNI = "DNI"
    CE = "CE"

class CarnetRequest(BaseModel):
    imageUrl: str
    signatureUrl: str
    number_document: str
    type_document: DocumentType
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
        600,
        480
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
        600, 
        480
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
        690,
        918
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

    generated_carnet_path=""

    if request.type_document == DocumentType.DNI:
        generated_carnet_path = carnet_service.generate(
        dni=request.number_document,
        nombres=request.names,
        apellidos=request.lastNames,
        nro_registro=request.nro_registro,
        firma_path=downloaded_signature,
        image_path=downloaded_photo
    ) 
    elif request.type_document == DocumentType.CE:
        generated_carnet_path = carnet_service.generate_ce(
        ce=request.number_document,
        nombres=request.names,
        apellidos=request.lastNames,
        nro_registro=request.nro_registro,
        firma_path=downloaded_signature,
        image_path=downloaded_photo
    ) 
    else :
        return {
            "error": "Tipo de documento no soportado"
        }


    

    generated_back_carnet_path = carnet_service.generate_back_carnet(
        dni=request.number_document,
        url_qr=request.url,
        output_folder="output"
    )

    generated_pdf_path = pdfService.PdfService.generate_pdf(
        front_image_path=generated_carnet_path,
        back_image_path=generated_back_carnet_path,
        output_folder="output",
        filename=f"{request.number_document}.pdf"
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