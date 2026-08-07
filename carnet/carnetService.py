from enum import Enum
import base64

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from io import BytesIO

from pydantic import BaseModel

from services.qrService import QrService
from .pdfService import PdfService

from .carnetConfig import (
    PHOTO_DNI, SIGNATURE_DNI, TEXT_DNI, APELLIDOS_BOX_DNI, NOMBRES_BOX_DNI,
    PHOTO_CE, SIGNATURE_CE, TEXT_CE, APELLIDOS_BOX_CE, NOMBRES_BOX_CE,
    FONT_SIZE, MAX_FONT_SIZE_TEXT, MIN_FONT_SIZE_TEXT, QR, FONT_SIZE_NUMBER,
    BACK_TEXT
)

class DocumentType(str, Enum):
    DNI = "DNI"
    CE = "CE"

class FileResponse(BaseModel):
    filename: str
    contentType: str
    data: str


class CarnetResponse(BaseModel):
    carnet: FileResponse
    backCarnet: FileResponse
    pdf: FileResponse

class CarnetService:
    TEMPLATE_DNI_PATH = "assets/dni_template.png"
    TEMPLATE_CE_PATH = "assets/ce_template.png"
    TEMPLATE_BACK_PATH = "assets/back_template.png"
    FONT_PATH = "assets/Montserrat-Bold.ttf"

    def __init__(self):
        try:
            self.font = ImageFont.truetype(
                self.FONT_PATH,
                FONT_SIZE
            )
            self.font_number = ImageFont.truetype(
                self.FONT_PATH,
                FONT_SIZE_NUMBER
            )
        except:
            self.font = ImageFont.load_default()
            self.font_number = ImageFont.load_default()

    def _resize_cover(
        self,
        image: Image.Image,
        width: int,
        height: int
        ) -> Image.Image:

        return ImageOps.fit(
            image,
            (width, height),
            method=Image.Resampling.LANCZOS,

            centering=(0.5, 0.5)
        )

    def _draw_text_in_box(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        box: dict,
        fill: str = "black",
        max_font_size: int = MAX_FONT_SIZE_TEXT,
        min_font_size: int = MIN_FONT_SIZE_TEXT,
        line_spacing: int = 2
    ):
        x = box["x"]
        y = box["y"]
        max_width = box["width"]
        max_height = box["height"]

        # Desde la fuente más grande hasta la más pequeña
        for font_size in range(max_font_size, min_font_size - 1, -1):

            font = ImageFont.truetype(
                self.FONT_PATH,
                font_size
            )

            # ---------- Intentar en una sola línea ----------
            bbox = draw.textbbox((0, 0), text, font=font)

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width <= max_width and text_height <= max_height:
                draw.text(
                    (x, y),
                    text,
                    fill=fill,
                    font=font
                )
                return

            # ---------- Intentar en varias líneas ----------
            words = text.split()

            lines = []
            current = ""

            for word in words:

                test = word if current == "" else f"{current} {word}"

                bbox = draw.textbbox((0, 0), test, font=font)
                width = bbox[2] - bbox[0]

                if width <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

            # Calcular altura total
            line_height = draw.textbbox((0, 0), "Ag", font=font)[3]
            total_height = len(lines) * line_height + (len(lines) - 1) * line_spacing

            if total_height <= max_height:

                yy = y

                for line in lines:

                    draw.text(
                        (x, yy),
                        line,
                        fill=fill,
                        font=font
                    )

                    yy += line_height + line_spacing

                return

        # Si nada encajó, usar el tamaño mínimo tal cual
        font = ImageFont.truetype(
            self.FONT_PATH,
            min_font_size
        )

        draw.text(
            (x, y),
            text,
            fill=fill,
            font=font
        )


    def generate(
        self,
        dni: str,
        nombres: str,
        apellidos: str,
        nro_registro: str,
        firma_bytes: bytes,
        image_bytes: bytes
    ) -> bytes:

        nombres = nombres.upper() 
        apellidos = apellidos.upper()

        carnet = Image.open(
            self.TEMPLATE_DNI_PATH
        ).convert("RGBA")

        draw = ImageDraw.Draw(carnet)

        foto = Image.open(
            BytesIO(image_bytes)
        ).convert("RGBA")

        foto = self._resize_cover(
            foto,
            PHOTO_DNI["width"],
            PHOTO_DNI["height"]
        )

        carnet.paste(
            foto,
            (
                PHOTO_DNI["x"],
                PHOTO_DNI["y"]
            )
        )

        firma = Image.open(
            BytesIO(firma_bytes)
        ).convert("RGBA")

        firma = self._resize_cover(
            firma,
            SIGNATURE_DNI["width"],
            SIGNATURE_DNI["height"]
        )

        carnet.paste(
            firma,
            (
                SIGNATURE_DNI["x"],
                SIGNATURE_DNI["y"]
            ),
            firma
        )

        draw.text(
            TEXT_DNI["dni"],
            dni,
            fill="black",
            font=self.font_number
        )

        draw.text(
            TEXT_DNI["registro"],
            nro_registro,
            fill="black",
            font=self.font_number
        )

        self._draw_text_in_box(
            draw,
            apellidos,
            APELLIDOS_BOX_DNI
        )

        self._draw_text_in_box(
            draw,
            nombres,
            NOMBRES_BOX_DNI
        )

        output = BytesIO()

        carnet.save(
            output,
            format="PNG"
        )

        return output.getvalue()

    def generate_ce(
        self,
        ce: str,
        nombres: str,
        apellidos: str,
        nro_registro: str,
        firma_bytes: bytes,
        image_bytes: bytes
    ) -> bytes:

        nombres = nombres.upper()
        apellidos = apellidos.upper()

        carnet = Image.open(
            self.TEMPLATE_CE_PATH
        ).convert("RGBA")

        draw = ImageDraw.Draw(carnet)

        foto = Image.open(
            BytesIO(image_bytes)
        ).convert("RGBA")

        foto = self._resize_cover(
            foto,
            PHOTO_CE["width"],
            PHOTO_CE["height"]
        )

        carnet.paste(
            foto,
            (
                PHOTO_CE["x"],
                PHOTO_CE["y"]
            )
        )

        firma = Image.open(
            BytesIO(firma_bytes)
        ).convert("RGBA")

        firma = self._resize_cover(
            firma,
            SIGNATURE_CE["width"],
            SIGNATURE_CE["height"]
        )

        carnet.paste(
            firma,
            (
                SIGNATURE_CE["x"],
                SIGNATURE_CE["y"]
            ),
            firma
        )

        draw.text(
            TEXT_CE["ce"],
            ce,
            fill="black",
            font=self.font_number
        )

        draw.text(
            TEXT_CE["registro"],
            nro_registro,
            fill="black",
            font=self.font_number
        )

        self._draw_text_in_box(
            draw,
            apellidos,
            APELLIDOS_BOX_CE
        )

        self._draw_text_in_box(
            draw,
            nombres,
            NOMBRES_BOX_CE
        )

        output = BytesIO()

        carnet.save(
            output,
            format="PNG"
        )

        return output.getvalue()


    def generate_back_carnet(
        self,
        url_qr: str,
        n_posterior: str,
        fecha: str
    ) -> bytes:

        carnet = Image.open(
            self.TEMPLATE_BACK_PATH
        ).convert("RGBA")

        qr_bytes = QrService.generate_qr(
            url=url_qr
        )

        qr = Image.open(
            BytesIO(qr_bytes)
        ).convert("RGBA")

        qr = self._resize_cover(
            qr,
            QR["width"],
            QR["height"]
        )

        carnet.paste(
            qr,
            (
                QR["x"],
                QR["y"]
            ),
            qr
        )

        draw = ImageDraw.Draw(carnet)
        try:
            back_font = ImageFont.truetype(
                self.FONT_PATH,
                BACK_TEXT["font_size"]
            )
        except OSError:
            back_font = ImageFont.load_default()

        draw.text(
            (BACK_TEXT["x"], BACK_TEXT["number_y"]),
            f"N° {n_posterior}",
            fill="black",
            font=back_font
        )
        draw.text(
            (BACK_TEXT["x"], BACK_TEXT["date_y"]),
            fecha,
            fill="black",
            font=back_font
        )

        output = BytesIO()

        carnet.save(
            output,
            format="PNG"
        )

        return output.getvalue()

    def carnet_create_orchestrator  (        
        self,
        type_document: DocumentType,
        number_document: str,
        nombres: str,
        apellidos: str,
        nro_registro: str,
        url_qr: str,
        n_posterior: str,
        fecha: str,
        firma_bytes: bytes,
        image_bytes: bytes) -> CarnetResponse:

        carnet_front_bytes = None

        if type_document == DocumentType.DNI:
            carnet_front_bytes = self.generate(
                dni=number_document,
                nombres=nombres,
                apellidos=apellidos,
                nro_registro=nro_registro,
                firma_bytes=firma_bytes,
                image_bytes=image_bytes
            )

        elif type_document == DocumentType.CE:
            carnet_front_bytes = self.generate_ce(
                ce=number_document,
                nombres=nombres,
                apellidos=apellidos,
                nro_registro=nro_registro,
                firma_bytes=firma_bytes,
                image_bytes=image_bytes
            )

        else:
            raise ValueError("Tipo de documento no soportado.")

        carnet_back_bytes = self.generate_back_carnet(
            url_qr=url_qr,
            n_posterior=n_posterior,
            fecha=fecha
        )

        pdf_bytes = PdfService.generate_pdf(
            front_image_bytes=carnet_front_bytes,
            back_image_bytes=carnet_back_bytes
        )

        return CarnetResponse(
            carnet = FileResponse(
                filename=f"{number_document}_carnet.png",
                contentType="image/png",
                data=base64.b64encode(carnet_front_bytes).decode("utf-8")
            ),
            backCarnet = FileResponse(
                filename=f"{number_document}_carnet_back.png",
                contentType="image/png",
                data=base64.b64encode(carnet_back_bytes).decode("utf-8")
            ),
            pdf = FileResponse(
                filename=f"{number_document}_carnet.pdf",
                contentType="application/pdf",
                data=base64.b64encode(pdf_bytes).decode("utf-8")
            )
        )

    def generate_carnet_preview(
        self,
        type_document: DocumentType,
        number_document: str,
        nombres: str,
        apellidos: str,
        firma_bytes: bytes,
        image_bytes: bytes
    ) -> FileResponse:
        carnet_front_bytes = None

        if type_document == DocumentType.DNI:
            carnet_front_bytes = self.generate(
                dni=number_document,
                nombres=nombres,
                apellidos=apellidos,
                nro_registro="00000",
                firma_bytes=firma_bytes,
                image_bytes=image_bytes
            )

        elif type_document == DocumentType.CE:
            carnet_front_bytes = self.generate_ce(
                ce=number_document,
                nombres=nombres,
                apellidos=apellidos,
                nro_registro="00000",
                firma_bytes=firma_bytes,
                image_bytes=image_bytes
            )

        else:
            raise ValueError("Tipo de documento no soportado.")

        return FileResponse(
            filename=f"{number_document}_carnet_preview.png",
            contentType="image/png",
            data=base64.b64encode(carnet_front_bytes).decode("utf-8")
        )

        
