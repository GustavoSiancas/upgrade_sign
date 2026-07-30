from io import BytesIO

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class PdfService:

    PAGE_W, PAGE_H = A4

    @classmethod
    def generate_pdf(
        cls,
        front_image_bytes: bytes,
        back_image_bytes: bytes
    ) -> bytes:

        output = BytesIO()

        pdf = canvas.Canvas(
            output,
            pagesize=A4
        )

        cls._add_page(
            pdf,
            front_image_bytes
        )

        cls._add_page(
            pdf,
            back_image_bytes
        )

        pdf.save()

        return output.getvalue()

    @classmethod
    def _add_page(
        cls,
        pdf: canvas.Canvas,
        image_bytes: bytes
    ) -> None:

        img = Image.open(
            BytesIO(image_bytes)
        )

        # Rotar 90° a la derecha
        img = img.rotate(
            -90,
            expand=True
        )

        iw, ih = img.size

        scale = min(
            cls.PAGE_W / iw,
            cls.PAGE_H / ih
        )

        new_w = iw * scale
        new_h = ih * scale

        x = 0
        y = (cls.PAGE_H - new_h) / 2

        image_buffer = BytesIO()

        img.save(
            image_buffer,
            format="PNG"
        )

        image_buffer.seek(0)

        pdf.drawImage(
            ImageReader(image_buffer),
            x,
            y,
            width=new_w,
            height=new_h,
            preserveAspectRatio=True,
            mask="auto"
        )

        pdf.showPage()