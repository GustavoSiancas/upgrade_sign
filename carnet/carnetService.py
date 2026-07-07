from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from qr.qrService import QrService

from .carnetConfig import PHOTO_DNI, SIGNATURE_CE, SIGNATURE_DNI, TEXT_DNI, PHOTO_CE, TEXT_CE, FONT_SIZE, QR


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
        except:
            self.font = ImageFont.load_default()

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

        draw.text(
            TEXT_DNI["dni"],
            dni,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT_DNI["apellidos"],
            apellidos,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT_DNI["nombres"],
            nombres,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT_DNI["registro"],
            nro_registro,
            fill="black",
            font=self.font
        )

        output = str(
            Path(output_folder) /
            f"{dni}.png"
        )

        carnet.save(output)

        return output
    
    def generate_ce(self,
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
            font=self.font
        )

        draw.text(
            TEXT_CE["apellidos"],
            apellidos,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT_CE["nombres"],
            nombres,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT_CE["registro"],
            nro_registro,
            fill="black",
            font=self.font
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

        # Generar QR
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

        # Eliminar el QR temporal
        Path(qr_path).unlink(missing_ok=True)

        return output
        
        