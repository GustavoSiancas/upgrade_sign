from fastapi import APIRouter, Response, UploadFile, File

from sign.upgradeSign_v1 import upgrade_sign_v1
from sign.upgradeSign_v2 import upgrade_sign_v2
from sign.upgradeSign_v3 import upgrade_sign_v3
from services.imageService import resize_image


router = APIRouter(
    prefix="/sign",
    tags=["Sign"]
)



@router.post("/upgrade-v1")
async def upgrade_signature(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v1(image_bytes)

    result_resized = resize_image(
        result,
        600,
        400
    )

    return Response(
        content=result_resized,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=signature.png"
        }
    )


@router.post("/upgrade-v2")
async def upgrade_signature_v2(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v2(image_bytes)

    result_resized = resize_image(
        result,
        600,
        400
    )

    return Response(
        content=result_resized,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=signature.png"
        }
    )

@router.post("/upgrade-v3")
async def upgrade_signature_v3(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v3(image_bytes)

    result_resized = resize_image(
        result,
        600,
        400
    )

    return Response(
        content=result_resized,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline; filename=signature.png"
        }
    )