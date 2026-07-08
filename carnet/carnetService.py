from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from qr.qrService import QrService

from .carnetConfig import (
    PHOTO_DNI, SIGNATURE_DNI, TEXT_DNI, APELLIDOS_BOX_DNI, NOMBRES_BOX_DNI,
    PHOTO_CE, SIGNATURE_CE, TEXT_CE, APELLIDOS_BOX_CE, NOMBRES_BOX_CE,
    FONT_SIZE, MAX_FONT_SIZE_TEXT, MIN_FONT_SIZE_TEXT, QR, FONT_SIZE_NUMBER
)


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
        firma_path: str,
        image_path: str,
        output_folder: str = "output"
    ) -> str:

        Path(output_folder).mkdir(exist_ok=True)

        carnet = Image.open(
            self.TEMPLATE_DNI_PATH
        ).convert("RGBA")

        draw = ImageDraw.Draw(carnet)

        # ======================
        # FOTO
        # ======================

        foto = Image.open(
            image_path
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

        # ======================
        # FIRMA
        # ======================

        firma = Image.open(
            firma_path
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

        # ======================
        # TEXTOS
        # ======================

        # DNI y registro: campos cortos y fijos, fuente estándar
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

        # Apellidos y nombres: largo variable, se autoajustan a la caja
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

        output = str(
            Path(output_folder) /
            f"{dni}.png"
        )

        carnet.save(output)

        return output

    def generate_ce(
        self,
        ce: str,
        nombres: str,
        apellidos: str,
        nro_registro: str,
        firma_path: str,
        image_path: str,
        output_folder: str = "output"
    ) -> str:

        Path(output_folder).mkdir(exist_ok=True)

        carnet = Image.open(
            self.TEMPLATE_CE_PATH
        ).convert("RGBA")

        draw = ImageDraw.Draw(carnet)

        # ======================
        # FOTO
        # ======================

        foto = Image.open(
            image_path
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

        # ======================
        # FIRMA
        # ======================

        firma = Image.open(
            firma_path
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

        # ======================
        # TEXTOS
        # ======================

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

        output = str(
            Path(output_folder) /
            f"{ce}.png"
        )

        carnet.save(output)

        return output

    def generate_back_carnet(
        self,
        dni: str,
        url_qr: str,
        output_folder: str = "output"
    ) -> str:

        Path(output_folder).mkdir(exist_ok=True)

        carnet = Image.open(
            self.TEMPLATE_BACK_PATH
        ).convert("RGBA")

        qr_path = str(
            Path(output_folder) / f"{dni}_qr.png"
        )

        QrService.generate_qr(
            url=url_qr,
            output_path=qr_path
        )

        qr = Image.open(qr_path).convert("RGBA")

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
            )
        )

        output = str(
            Path(output_folder) / f"{dni}_back.png"
        )

        carnet.save(output)

        Path(qr_path).unlink(missing_ok=True)

        return output