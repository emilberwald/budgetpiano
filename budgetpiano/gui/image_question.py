import cv2
import numpy
import math
import tkinter
import tkinter.simpledialog
import tkinter.colorchooser
import PIL, PIL.Image, PIL.ImageTk


class ImageQuestion(tkinter.simpledialog.Dialog):
    def __init__(self, *, image, parent=None):
        self.image = image
        if parent is None:
            self.parent = tkinter.Tk()
            self.parent.withdraw()
        super().__init__(parent=self.parent, title="Image Question")

    def body(self, master):
        self.canvas = tkinter.Canvas(master, width=self.image.shape[1], height=self.image.shape[0])
        self.canvas.configure(scrollregion=self.canvas.bbox(tkinter.ALL))
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.image_tk = PIL.ImageTk.PhotoImage(
            PIL.Image.fromarray(
                cv2.cvtColor(
                    self.image,
                    cv2.COLOR_BGR2RGB,
                )
            ),
            master=master,
        )
        self.image_tk_id = self.canvas.create_image(
            0,
            0,
            image=self.image_tk,
            anchor="nw",
        )

    def apply(self):
        self.result = True


def ask_image_question(image):
    return ImageQuestion(image=image).result
