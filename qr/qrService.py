from pathlib import Path
import qrcode


class QrService:
    @staticmethod
    def generate_qr(url: str, output_path: str) -> str:
        """
        Genera un código QR a partir de una URL y lo guarda en disco.

        Args:
            url (str): URL que contendrá el QR.
            output_path (str): Ruta donde se guardará la imagen.

        Returns:
            str: Ruta del archivo generado.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )

        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

        return output_path