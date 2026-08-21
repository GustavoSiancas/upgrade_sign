from datetime import date
from io import BytesIO

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError
import requests

from services.certificatePdfService import CertificatePdfService
from services.signerVeronicaQuispe import SignerVeronicaQuispeService


router = APIRouter(
    prefix="/signer-veronica-quispe",
    tags=["Signer Veronica Quispe"],
)

DEFAULT_SIGNER = "VERÓNICA EDITH QUISPE GUTIÉRREZ"


@router.post("", response_class=StreamingResponse)
def generate_signed_pdf(
    nameIncorp: str = Form(..., min_length=2, max_length=150),
    numero_cal: str = Form(..., min_length=1, max_length=30),
    link: str = Form(...),
    fecha: date = Form(...),
    pdf_link: str = Form(...),
) -> StreamingResponse:
    try:
        qr_link = str(TypeAdapter(AnyHttpUrl).validate_python(link))
        source_pdf_link = str(TypeAdapter(AnyHttpUrl).validate_python(pdf_link))
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="link y pdf_link deben ser URLs HTTP válidas.") from exc

    certificate_image = SignerVeronicaQuispeService.generate(
        name_incorp=nameIncorp.strip(),
        signer=DEFAULT_SIGNER,
        numero_cal=numero_cal.strip(),
        link=qr_link,
        fecha=fecha,
    )

    try:
        final_pdf = CertificatePdfService.download_and_append(
            pdf_link=source_pdf_link,
            certificate_image=certificate_image,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="No se pudo descargar el PDF indicado.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    safe_cal = "".join(char for char in numero_cal if char.isalnum() or char in "-_")
    headers = {
        "Content-Disposition": f'attachment; filename="documento_cal_{safe_cal or "final"}.pdf"'
    }
    return StreamingResponse(
        BytesIO(final_pdf),
        media_type="application/pdf",
        headers=headers,
    )
