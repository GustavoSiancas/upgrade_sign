from io import BytesIO
import qrcode


class QrService:
    @staticmethod
    def generate_qr(url: str) -> bytes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        output = BytesIO()

        img.save(
            output,
            format="PNG"
        )

        return output.getvalue()