import pathlib

import tkinter
import tkinter.filedialog


def ask_for_image():
    root = tkinter.Tk()
    try:
        root.title("Select Image of Instrument")
        file_path = tkinter.filedialog.askopenfilename(
            filetypes=[
                (
                    "All Image Files",
                    "*.bmp;*.dib;*.jpeg;*.jpg;*.jpe;*.jp2;*.png;*.webp;*.ppm;*.pxm;*.pbm;*.pgm;*.pnm;*.sr;*.ras;*.tiff;*.tif;*.exr;*.hdr;*.pic",
                ),
                ("Bitmap", "*.bmp;*.dib"),
                ("Joint Photographic Experts Group", "*.jpeg;*.jpg;*.jpe"),
                ("JPEG 2000", "*.jp2"),
                ("Portable Network Graphics", "*.png"),
                ("WebP", "*.webp"),
                ("Portable Pixmap", "*.ppm"),
                ("Portable Bitmap", "*.pbm"),
                ("Portable Greymap", "*.pgm"),
                ("Portable Anymap", "*.pnm; *.pxm"),
                ("Sun Raster", "*.sr;*.ras"),
                ("TIFF", "*.tiff;*.tif"),
                ("OpenEXR", "*.exr"),
                ("Radiance HDR", "*.hdr;*.pic"),
            ]
        )
        return pathlib.Path(file_path)
    finally:
        root.destroy()
