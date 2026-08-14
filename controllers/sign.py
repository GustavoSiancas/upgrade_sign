import base64

from fastapi import APIRouter, Response, UploadFile, File

from sign.upgradeSign_v1 import upgrade_sign_v1
from sign.upgradeSign_v2 import upgrade_sign_v2
from sign.upgradeSign_v3 import upgrade_sign_v3
from services.imageService import resize_signature

router = APIRouter(
    prefix="/sign",
    tags=["Sign"]
)


def _signature_json(images: dict[str, bytes]) -> dict[str, str]:
    return {
        "transparent": base64.b64encode(images["transparent"]).decode("ascii"),
        "white": base64.b64encode(images["white"]).decode("ascii")
    }


@router.post("/upgrade-v1")
async def upgrade_signature(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v1(image_bytes)

    result_resized = resize_signature(
        result,
        600,
        480
    )

    return _signature_json(result_resized)


@router.post("/upgrade-v2")
async def upgrade_signature_v2(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v2(image_bytes)

    result_resized = resize_signature(
        result,
        600,
        480
    )

    return _signature_json(result_resized)

@router.post("/upgrade-v3")
async def upgrade_signature_v3(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    result = upgrade_sign_v3(image_bytes)

    result_resized = resize_signature(
        result,
        600,
        480
    )

    return _signature_json(result_resized)
