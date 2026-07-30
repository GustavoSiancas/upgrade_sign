from fastapi import APIRouter, UploadFile, File, Response

from services.imageService import resize_image

router = APIRouter(
    prefix="/resize",
    tags=["Resize Images"]
)


@router.post("/signature")
async def resize_signature(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = resize_image(
        image_bytes,
        600,
        480
    )

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=signature.png"
        }
    )


@router.post("/photo")
async def resize_photo(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = resize_image(
        image_bytes,
        690,
        918
    )

    return Response(
        content=result,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=photo.png"
        }
    )