from fastapi import APIRouter, UploadFile, File, Form

from carnet.carnetService import (
    CarnetService,
    CarnetResponse,
    DocumentType,
    FileResponse
)

router = APIRouter(
    prefix="/carnet",
    tags=["Carnet"]
)


@router.post(
    "",
    response_model=CarnetResponse
)
async def generate_carnet(
    photo: UploadFile = File(...),
    signature: UploadFile = File(...),
    type_document: DocumentType = Form(...),
    number_document: str = Form(...),
    names: str = Form(...),
    last_names: str = Form(...),
    nro_registro: str = Form(...),
    url_qr: str = Form(...),
    n_posterior: str = Form(...),
    fecha: str = Form(...)
):

    photo_bytes = await photo.read()
    signature_bytes = await signature.read()

    carnet_service = CarnetService()

    return carnet_service.carnet_create_orchestrator(
        type_document=type_document,
        number_document=number_document,
        nombres=names,
        apellidos=last_names,
        nro_registro=nro_registro,
        url_qr=url_qr,
        n_posterior=n_posterior,
        fecha=fecha,
        firma_bytes=signature_bytes,
        image_bytes=photo_bytes
    )


@router.post(
    "/preview",
    response_model=FileResponse
)
async def generate_carnet_preview(
    photo: UploadFile = File(...),
    signature: UploadFile = File(...),
    type_document: DocumentType = Form(...),
    number_document: str = Form(...),
    names: str = Form(...),
    last_names: str = Form(...)
):

    photo_bytes = await photo.read()
    signature_bytes = await signature.read()

    carnet_service = CarnetService()

    return carnet_service.generate_carnet_preview(
        type_document=type_document,
        number_document=number_document,
        nombres=names,
        apellidos=last_names,
        firma_bytes=signature_bytes,
        image_bytes=photo_bytes
    )
