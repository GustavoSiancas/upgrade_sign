import base64

from fastapi import APIRouter, UploadFile, File

from sign.upgradeSign_v1 import upgrade_sign_v1
from sign.upgradeSign_v2 import upgrade_sign_v2
from sign.upgradeSign_v3 import upgrade_sign_v3
from services.imageService import resize_signature

router = APIRouter(
    prefix="/sign",
    tags=["Sign"]
)


def _signature_json(
    normal: bytes,
    upgraded: bytes,
    final: bytes
) -> dict[str, str]:
    return {
        "normal": base64.b64encode(normal).decode("ascii"),
        "upgraded": base64.b64encode(upgraded).decode("ascii"),
        "final": base64.b64encode(final).decode("ascii")
    }


@router.post("/upgrade-v1")
async def upgrade_signature(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    upgraded = upgrade_sign_v1(image_bytes)

    resized = resize_signature(
        upgraded,
        600,
        480
    )

    return _signature_json(image_bytes, upgraded, resized["transparent"])


@router.post("/upgrade-v2")
async def upgrade_signature_v2(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    upgraded = upgrade_sign_v2(image_bytes)

    resized = resize_signature(
        upgraded,
        600,
        480
    )

    return _signature_json(image_bytes, upgraded, resized["transparent"])


@router.post("/upgrade-v3")
async def upgrade_signature_v3(
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    upgraded = upgrade_sign_v3(image_bytes)

    resized = resize_signature(
        upgraded,
        600,
        480
    )

    return _signature_json(image_bytes, upgraded, resized["transparent"])
