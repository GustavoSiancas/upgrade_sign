import os
from pathlib import Path

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Remover Fondo Firma")

        # Crear carpetas automáticamente
        self.uploads_dir = Path("uploads")
        self.processed_dir = Path("processed")

        self.uploads_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)

        self.original_label = tk.Label(root, text="Original")
        self.original_label.grid(row=0, column=0, padx=10, pady=10)

        self.result_label = tk.Label(root, text="Resultado")
        self.result_label.grid(row=0, column=1, padx=10, pady=10)

        self.original_img_label = tk.Label(root)
        self.original_img_label.grid(row=1, column=0)

        self.result_img_label = tk.Label(root)
        self.result_img_label.grid(row=1, column=1)

        tk.Button(
            root,
            text="Seleccionar Firma",
            command=self.procesar
        ).grid(row=2, column=0, columnspan=2, pady=20)

        self.result_rgba = None

    def procesar(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Imagen", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        if not path:
            return

        # Nombre del archivo
        filename = os.path.basename(path)

        # Guardar copia del original en uploads
        upload_path = self.uploads_dir / filename
        Image.open(path).save(upload_path)

        # Mostrar original
        original = Image.open(path)
        original.thumbnail((350, 250))

        self.original_photo = ImageTk.PhotoImage(original)
        self.original_img_label.config(image=self.original_photo)

        # Leer imagen con OpenCV
        img = cv2.imread(path)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        _, thresh = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        kernel = np.ones((2, 2), np.uint8)

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            kernel
        )

        # Crear PNG con transparencia
        result = np.zeros(
            (thresh.shape[0], thresh.shape[1], 4),
            dtype=np.uint8
        )

        result[:, :, 0] = 0
        result[:, :, 1] = 0
        result[:, :, 2] = 0
        result[:, :, 3] = thresh

        self.result_rgba = result

        # Vista previa sobre fondo gris
        preview = np.full(
            (result.shape[0], result.shape[1], 3),
            220,
            dtype=np.uint8
        )

        alpha = result[:, :, 3] / 255.0

        for c in range(3):
            preview[:, :, c] = (
                alpha * result[:, :, c]
                + (1 - alpha) * preview[:, :, c]
            )

        preview = Image.fromarray(preview.astype(np.uint8))
        preview.thumbnail((350, 250))

        self.result_photo = ImageTk.PhotoImage(preview)
        self.result_img_label.config(image=self.result_photo)

        # Guardar resultado en processed
        output_path = (
            self.processed_dir /
            f"{Path(filename).stem}_transparent.png"
        )

        cv2.imwrite(str(output_path), result)

        print(f"Original guardada en: {upload_path}")
        print(f"Procesada guardada en: {output_path}")


root = tk.Tk()
App(root)
root.mainloop()