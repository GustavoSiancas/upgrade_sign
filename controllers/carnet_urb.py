from fastapi import APIRouter
from pydantic import BaseModel

from services.downloadImage import DownloadImageService

from carnet.carnetService import (
    CarnetService,
    CarnetResponse,
    DocumentType,
    FileResponse
)

router = APIRouter(
    prefix="/carnet-urb",
    tags=["Carnet-urb"]
)


class CarnetRequest(BaseModel):
    photo_url: str
    signature_url: str
    type_document: DocumentType
    number_document: str
    names: str
    last_names: str
    nro_registro: str
    n_posterior: str
    fecha: str
    url_qr: str


class CarnetPreviewRequest(BaseModel):
    photo_url: str
    signature_url: str
    type_document: DocumentType
    number_document: str
    names: str
    last_names: str


@router.post("", response_model=CarnetResponse)
def generate_carnet(request: CarnetRequest):
    photo_bytes = DownloadImageService.download_as_png_bytes(request.photo_url)
    signature_bytes = DownloadImageService.download_as_png_bytes(request.signature_url)

    return CarnetService().carnet_create_orchestrator(
        type_document=request.type_document,
        number_document=request.number_document,
        nombres=request.names,
        apellidos=request.last_names,
        nro_registro=request.nro_registro,
        url_qr=request.url_qr,
        n_posterior=request.n_posterior,
        fecha=request.fecha,
        firma_bytes=signature_bytes,
        image_bytes=photo_bytes,
    )


@router.post("/preview", response_model=FileResponse)
def generate_carnet_preview(request: CarnetPreviewRequest):
    photo_bytes = DownloadImageService.download_as_png_bytes(request.photo_url)
    signature_bytes = DownloadImageService.download_as_png_bytes(request.signature_url)

    return CarnetService().generate_carnet_preview(
        type_document=request.type_document,
        number_document=request.number_document,
        nombres=request.names,
        apellidos=request.last_names,
        firma_bytes=signature_bytes,
        image_bytes=photo_bytes,
    )