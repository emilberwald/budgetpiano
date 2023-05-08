import cv2
import numpy
import math
import tkinter
import tkinter.simpledialog
import tkinter.colorchooser
import PIL, PIL.Image, PIL.ImageTk


def _draw_keys(*, left, top, width, height, scale, image, fill_color, border_color, border_thickness):
    start = (int(scale * left), int(scale * top))
    end = (start[0] + int(scale * width), start[1] + int(scale * height))
    cv2.rectangle(image, start, end, fill_color, cv2.FILLED)
    cv2.rectangle(image, start, end, border_color, border_thickness)


def _get_piano(
    white_key_width_px: int = 10,
    nof_keys: int = 88,
    start_key_pitchclass: int = 9,
    white_key_color=(255, 255, 255),
    black_key_color=(0, 0, 0),
    red_velvet_color=(0, 0, 77),
    border_color=(128, 128, 128),
    background_color=(128, 128, 128),
):
    red_velvet_height = 0.2
    white_key_width = 2.25
    white_key_height = 14.6
    white_key_narrow_space = 0.1
    white_key_large_space = 0.125
    black_key_width = 1.40
    black_key_height = 9.8
    black_key_offsets = [1.3, 1.8, 1.2, 1.6, 1.9]

    white_key_starts = []
    black_key_starts = []
    white_key_pitchclasses = [0, 2, 4, 5, 7, 9, 11]
    P1 = white_key_pitchclasses[0]
    M2 = white_key_pitchclasses[1]
    M3 = white_key_pitchclasses[2]
    P4 = white_key_pitchclasses[3]
    P5 = white_key_pitchclasses[4]
    M6 = white_key_pitchclasses[5]
    M7 = white_key_pitchclasses[6]
    wide_space_before_pitchclass = [P1, P4]
    black_key_pitchclasses = [P1 + 1, M2 + 1, P4 + 1, P5 + 1, M6 + 1]

    white_key_start_offset = 0.0
    for key_no in range(nof_keys):
        key_pitchclass = (start_key_pitchclass + key_no) % 12
        if key_pitchclass in white_key_pitchclasses:
            space_after = (
                white_key_large_space if key_pitchclass in wide_space_before_pitchclass else white_key_narrow_space
            )
            if len(white_key_starts) > 0:
                white_key_starts.append(white_key_starts[-1] + white_key_width + space_after)
            else:
                white_key_starts.append(white_key_start_offset)
        else:
            black_key_offset = black_key_offsets[black_key_pitchclasses.index(key_pitchclass)]
            if len(white_key_starts) > 0:
                black_key_starts.append(white_key_starts[-1] + black_key_offset)
            else:
                black_key_starts.append(black_key_offset)
                white_key_start_offset = white_key_width + white_key_narrow_space

    width = 0.0
    if len(white_key_starts) > 0:
        width = max(width, white_key_starts[-1] + white_key_width)
    if len(black_key_starts) > 0:
        width = max(width, black_key_starts[-1] + black_key_width)
    height = white_key_height + red_velvet_height

    scale = white_key_width_px / white_key_width

    image = numpy.ndarray((max(1, math.ceil(scale * height)), max(1, math.ceil(scale * width)), 3), numpy.uint8)
    image[..., :] = background_color
    width_px = image.shape[1]

    cv2.rectangle(image, (0, 0), (width_px, int(scale * red_velvet_height)), red_velvet_color, cv2.FILLED)
    for white_key_start in white_key_starts:
        _draw_keys(
            left=white_key_start,
            top=red_velvet_height,
            width=white_key_width,
            height=white_key_height,
            scale=scale,
            fill_color=white_key_color,
            image=image,
            border_color=border_color,
            border_thickness=1,
        )
        # TODO: the white keys are rounded at bottom

    for black_key_start in black_key_starts:
        _draw_keys(
            left=black_key_start,
            top=red_velvet_height,
            width=black_key_width,
            height=black_key_height,
            scale=scale,
            fill_color=black_key_color,
            image=image,
            border_color=border_color,
            border_thickness=1,
        )

    return image


class PianoPicker(tkinter.simpledialog.Dialog):
    def __init__(self, *, width: int, height: int, parent=None):
        self.width = width
        self.height = height
        self.image = None
        if parent is None:
            self.parent = tkinter.Tk()
            self.parent.withdraw()

        # Set up buttons to choose colors
        self.bgr_colors = {
            "white_key_color": (255, 255, 255),
            "black_key_color": (0, 0, 0),
            "red_velvet_color": (0, 0, 70),
            "border_color": (128, 128, 128),
            "background_color": (70, 70, 70),
        }

        super().__init__(parent=self.parent, title="Piano App")

    def body(self, master):
        self.image_tk = None
        self.image_tk_id = None

        # Set up left part of the window to display the image
        self.canvas_frame = tkinter.Frame(master, width=int(self.width * 0.8), height=self.height)
        self.canvas_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.canvas = tkinter.Canvas(self.canvas_frame, width=int(self.width * 0.8), height=self.height)
        hbar = tkinter.Scrollbar(self.canvas_frame, orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        hbar.config(command=self.canvas.xview)
        vbar = tkinter.Scrollbar(self.canvas_frame, orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.configure(scrollregion=self.canvas.bbox(tkinter.ALL))
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        # Set up right part of the window with color pickers and sliders
        self.settings_frame = tkinter.Frame(master, width=int(self.width * 0.2), height=self.height)
        self.settings_frame.pack(side=tkinter.RIGHT)

        # White key width slider
        self.width_label = tkinter.Label(self.settings_frame, text="White Key Width (px):")
        self.width_label.pack()
        self.width_slider = tkinter.Scale(
            self.settings_frame,
            from_=1,
            to=100,
            resolution=1,
            length=int(self.width * 0.2),
            orient="horizontal",
            command=self._update_image,
        )
        self.width_slider.pack()
        self.width_slider.set(10)

        # Number of keys slider
        self.nof_keys_label = tkinter.Label(self.settings_frame, text="Number of Keys:")
        self.nof_keys_label.pack()
        self.nof_keys_slider = tkinter.Scale(
            self.settings_frame,
            from_=1,
            to=128,
            resolution=1,
            length=int(self.width * 0.2),
            orient="horizontal",
            command=self._update_image,
        )
        self.nof_keys_slider.pack()
        self.nof_keys_slider.set(88)

        # Start key pitchclass slider
        self.start_key_label = tkinter.Label(self.settings_frame, text="Start Key Pitchclass:")
        self.start_key_label.pack()
        self.start_key_slider = tkinter.Scale(
            self.settings_frame,
            from_=0,
            to=11,
            resolution=1,
            length=int(self.width * 0.2),
            orient="horizontal",
            command=self._update_image,
        )
        self.start_key_slider.pack()
        self.start_key_slider.set(9)

        self.color_pickers = dict()
        for key, bgr in self.bgr_colors.items():
            self.color_pickers[key] = tkinter.Button(
                self.settings_frame,
                text=f"{key}",
                command=self._choose_color(key, bgr),
                bg=self._get_hexcolor(bgr[::-1]),
                fg=self._get_hexcolor(self._get_contrast_color(bgr[::-1])),
            )
            self.color_pickers[key].pack(anchor="w")

        return master

    def apply(self):
        self.result = self.image

    def _update_image(self, *args, **kwargs):
        self.image = _get_piano(
            self.width_slider.get(),
            self.nof_keys_slider.get(),
            self.start_key_slider.get(),
            **self.bgr_colors,
        )
        self.image_tk = PIL.ImageTk.PhotoImage(
            PIL.Image.fromarray(
                cv2.cvtColor(
                    self.image,
                    cv2.COLOR_BGR2RGB,
                )
            )
        )
        if self.image_tk_id is None:
            self.image_tk_id = self.canvas.create_image(
                0,
                0,
                image=self.image_tk,
                anchor="nw",
            )
        else:
            self.canvas.itemconfig(self.image_tk_id, image=self.image_tk)
            self.canvas.configure(scrollregion=self.canvas.bbox(tkinter.ALL))

    def _get_hexcolor(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _get_contrast_color(self, rgb):
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        if luminance > 0.5:
            return (0, 0, 0)
        else:
            return (255, 255, 255)

    def _choose_color(self, key, default_value):
        def _choose_color_implementation():
            rgb, hexcolor = tkinter.colorchooser.askcolor(title=f"Color Picker: {key}", initialcolor=default_value)
            if rgb is not None:
                self.bgr_colors[key] = rgb[::-1]
                self.color_pickers[key].configure(bg=hexcolor, fg=self._get_hexcolor(self._get_contrast_color(rgb)))
                self._update_image()

        return _choose_color_implementation


def ask_for_piano_image():
    return PianoPicker(width=800, height=600).result


if __name__ == "__main__":
    image = ask_for_piano_image()
    pass
