from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from .carnetConfig import PHOTO, SIGNATURE, TEXT, FONT_SIZE


class CarnetService:

    TEMPLATE_PATH = "assets/template.png"
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
            self.TEMPLATE_PATH
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
            PHOTO["width"],
            PHOTO["height"]
        )

        carnet.paste(
            foto,
            (
                PHOTO["x"],
                PHOTO["y"]
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
            SIGNATURE["width"],
            SIGNATURE["height"]
        )

        carnet.paste(
            firma,
            (
                SIGNATURE["x"],
                SIGNATURE["y"]
            ),
            firma
        )

        # ======================
        # TEXTOS
        # ======================

        draw.text(
            TEXT["dni"],
            dni,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT["apellidos"],
            apellidos,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT["nombres"],
            nombres,
            fill="black",
            font=self.font
        )

        draw.text(
            TEXT["registro"],
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