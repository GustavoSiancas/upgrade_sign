from io import BytesIO

import requests
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class CertificatePdfService:
    MAX_PDF_BYTES = 25 * 1024 * 1024

    @classmethod
    def download_pdf(cls, pdf_link: str, timeout: int = 30) -> bytes:
        with requests.get(pdf_link, timeout=timeout, stream=True) as response:
            response.raise_for_status()
            output = BytesIO()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                output.write(chunk)
                if output.tell() > cls.MAX_PDF_BYTES:
                    raise ValueError("El PDF supera el límite permitido de 25 MB.")

        pdf_bytes = output.getvalue()
        if not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("El contenido descargado no es un PDF válido.")
        return pdf_bytes

    @staticmethod
    def _image_as_pdf(image_bytes: bytes) -> bytes:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()

        page_width, page_height = A4
        output = BytesIO()
        pdf = canvas.Canvas(output, pagesize=A4)

        with Image.open(BytesIO(image_bytes)) as image:
            image_width, image_height = image.size
        scale = min(page_width / image_width, page_height / image_height)
        width = image_width * scale
        height = image_height * scale
        x = (page_width - width) / 2
        y = (page_height - height) / 2

        pdf.drawImage(
            ImageReader(BytesIO(image_bytes)),
            x,
            y,
            width=width,
            height=height,
            preserveAspectRatio=True,
            mask="auto",
        )
        pdf.showPage()
        pdf.save()
        return output.getvalue()

    @classmethod
    def append_certificate(cls, pdf_bytes: bytes, certificate_image: bytes) -> bytes:
        try:
            source_reader = PdfReader(BytesIO(pdf_bytes))
            certificate_reader = PdfReader(BytesIO(cls._image_as_pdf(certificate_image)))
            writer = PdfWriter()
            for page in source_reader.pages:
                writer.add_page(page)
            writer.add_page(certificate_reader.pages[0])

            output = BytesIO()
            writer.write(output)
            return output.getvalue()
        except Exception as exc:
            raise ValueError("No se pudo procesar el PDF descargado.") from exc

    @classmethod
    def download_and_append(cls, pdf_link: str, certificate_image: bytes) -> bytes:
        pdf_bytes = cls.download_pdf(pdf_link)
        return cls.append_certificate(pdf_bytes, certificate_image)
