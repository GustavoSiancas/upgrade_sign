from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile
import os


class PdfService:

    PAGE_W, PAGE_H = A4

    @classmethod
    def generate_pdf(
        cls,
        front_image_path: str,
        back_image_path: str,
        output_folder: str = "output",
        filename: str | None = None
    ) -> str:

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = Path(front_image_path).stem + ".pdf"

        output_path = Path(output_folder) / filename

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4
        )

        cls._add_page(pdf, front_image_path)
        cls._add_page(pdf, back_image_path)

        pdf.save()

        return str(output_path)

    @classmethod
    def _add_page(
        cls,
        pdf: canvas.Canvas,
        image_path: str
    ) -> None:

        img = Image.open(image_path)

        # Rotar 90° a la derecha
        img = img.rotate(-90, expand=True)

        iw, ih = img.size

        scale = min(
            cls.PAGE_W / iw,
            cls.PAGE_H / ih
        )

        new_w = iw * scale
        new_h = ih * scale

        x = 0
        y = (cls.PAGE_H - new_h) / 2

        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ) as tmp:
            temp_name = tmp.name

        try:
            img.save(temp_name)

            pdf.drawImage(
                temp_name,
                x,
                y,
                width=new_w,
                height=new_h,
                preserveAspectRatio=True,
                mask="auto"
            )

            pdf.showPage()

        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)    