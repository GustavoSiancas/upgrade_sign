import base64

from fastapi import APIRouter, UploadFile, File, Response

from services.imageService import resize_image, resize_signature

router = APIRouter(
    prefix="/resize",
    tags=["Resize Images"]
)


@router.post("/signature")
async def resize_signature_controller(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = resize_signature(
        image_bytes,
        600, # Ancho máximo de la firma en el carnet
        480  # Alto máximo de la firma en el carnet
    )

    return {
        "transparent": base64.b64encode(result["transparent"]).decode("ascii"),
        "white": base64.b64encode(result["white"]).decode("ascii")
    }


@router.post("/photo")
async def resize_photo_controller(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = resize_image(
        image_bytes,
        690, # Ancho máximo de la foto en el carnet
        918  # Alto máximo de la foto en el carnet
    )

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=photo.png"
        }
    )
