import base64
from datetime import date
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

from services.qrService import QrService


class SignerVeronicaQuispeFileResponse(BaseModel):
    filename: str
    contentType: str
    data: str


class SignerVeronicaQuispeService:
    """Genera la constancia de inscripcion del CAL como una imagen PNG."""

    WIDTH = 516
    HEIGHT = 622
    NAVY = (17, 48, 94)
    MONTHS = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    )
    SIGNATURE_PATH = Path(__file__).resolve().parent.parent / "assets" / "sign.png"

    @staticmethod
    def _font(size: int, bold: bool = False, sans: bool = False) -> ImageFont.FreeTypeFont:
        project_assets = Path(__file__).resolve().parent.parent / "assets"
        if sans and bold:
            candidates = [project_assets / "Montserrat-Bold.ttf"]
        elif sans:
            candidates = [
                Path("C:/Windows/Fonts/arial.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]
        elif bold:
            candidates = [
                Path("C:/Windows/Fonts/timesbd.ttf"),
                Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
            ]
        else:
            candidates = [
                Path("C:/Windows/Fonts/times.ttf"),
                Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            ]

        for path in candidates:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        return ImageFont.load_default()

    @staticmethod
    def _centered_text(
        draw: ImageDraw.ImageDraw,
        y: int,
        text: str,
        font: ImageFont.ImageFont,
        fill: tuple[int, int, int] | str = "black",
    ) -> None:
        box = draw.textbbox((0, 0), text, font=font)
        x = (SignerVeronicaQuispeService.WIDTH - (box[2] - box[0])) // 2
        draw.text((x, y), text, font=font, fill=fill)

    @classmethod
    def _fit_centered_text(
        cls,
        draw: ImageDraw.ImageDraw,
        y: int,
        text: str,
        max_width: int,
        max_size: int,
        min_size: int,
        sans: bool = False,
    ) -> None:
        for size in range(max_size, min_size - 1, -1):
            font = cls._font(size, bold=True, sans=sans)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= max_width:
                cls._centered_text(draw, y, text, font)
                return
        cls._centered_text(draw, y, text, cls._font(min_size, bold=True, sans=sans))

    @staticmethod
    def _wrap_text(
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
    ) -> list[str]:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = word if not current else f"{current} {word}"
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    @classmethod
    def _paste_signature(cls, image: Image.Image) -> None:
        with Image.open(cls.SIGNATURE_PATH) as source:
            signature = source.convert("RGBA")
            alpha_box = signature.getchannel("A").getbbox()
            if alpha_box is None:
                raise ValueError("El archivo assets/sign.png no contiene una firma visible.")
            signature = signature.crop(alpha_box)
            signature.thumbnail((190, 45), Image.Resampling.LANCZOS)
            x = (cls.WIDTH - signature.width) // 2
            image.paste(signature, (x, 476), signature)

    @classmethod
    def _format_date(cls, value: date) -> str:
        return f"Lima, {value.day} de {cls.MONTHS[value.month - 1]} de {value.year}"

    @classmethod
    def generate(
        cls,
        name_incorp: str,
        signer: str,
        numero_cal: str,
        link: str,
        fecha: date,
    ) -> bytes:
        image = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), "white")
        draw = ImageDraw.Draw(image)

        # Marco y encabezado institucional.
        draw.rectangle((35, 37, 480, 602), outline=cls.NAVY, width=2)
        cls._centered_text(
            draw, 69, "Ilustre Colegio de Abogados de Lima",
            cls._font(20, bold=True), cls.NAVY
        )

        body_font = cls._font(16)
        draw.text((63, 116), "LA SECRETARIA GENERAL, que suscribe, CERTIFICA:", font=body_font, fill="black")
        certification = (
            f"El Colegio de Abogados de Lima colegia a {name_incorp.strip()} "
            f"bajo el N.° {numero_cal}."
        )
        for index, line in enumerate(cls._wrap_text(draw, certification, body_font, 390)):
            draw.text((63, 140 + index * 22), line, font=body_font, fill="black")
        draw.text((63, 212), cls._format_date(fecha), font=body_font, fill="black")

        qr_bytes = QrService.generate_qr(link)
        with Image.open(BytesIO(qr_bytes)) as qr_source:
            qr = qr_source.convert("RGB").resize((200, 200), Image.Resampling.NEAREST)
        image.paste(qr, (158, 240))

        cls._centered_text(
            draw, 450, "Verifique escaneando el código QR",
            cls._font(11, sans=True), (105, 105, 105)
        )

        cls._paste_signature(image)
        draw.line((63, 519, 455, 519), fill="black", width=2)
        cls._centered_text(
            draw, 525, "Firmado digitalmente por",
            cls._font(11, sans=True), (100, 100, 100)
        )
        cls._fit_centered_text(
            draw, 542, signer.upper(), 370, 14, 9, sans=True
        )
        cls._centered_text(draw, 563, "Secretaria General", cls._font(12, sans=True))

        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    @classmethod
    def create_response(
        cls,
        name_incorp: str,
        signer: str,
        numero_cal: str,
        link: str,
        fecha: date,
    ) -> SignerVeronicaQuispeFileResponse:
        image_bytes = cls.generate(name_incorp, signer, numero_cal, link, fecha)
        safe_cal = "".join(character for character in numero_cal if character.isalnum() or character in "-_")
        return SignerVeronicaQuispeFileResponse(
            filename=f"constancia_cal_{safe_cal or 'documento'}.png",
            contentType="image/png",
            data=base64.b64encode(image_bytes).decode("ascii"),
        )
