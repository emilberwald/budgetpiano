import cv2
import numpy
import math


def _draw_keys(*, left, top, width, height, scale, image, fill_color, border_color, border_thickness):
    start = (int(scale * left), int(scale * top))
    end = (start[0] + int(scale * width), start[1] + int(scale * height))
    cv2.rectangle(image, start, end, fill_color, cv2.FILLED)
    cv2.rectangle(image, start, end, border_color, border_thickness)


def get_piano(
    white_key_width_px: int = 10,
    nof_keys: int = 88,
    start_key_pitchclass: int = 9,
    white_key_color=(255, 255, 255),
    black_key_color=(0, 0, 0),
    red_velvet_color=(0, 0, 77),
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

    for key_no in range(nof_keys):
        key_pitchclass = (start_key_pitchclass + key_no) % 12
        if key_pitchclass in white_key_pitchclasses:
            space_after = (
                white_key_large_space if key_pitchclass in wide_space_before_pitchclass else white_key_narrow_space
            )
            if len(white_key_starts) > 0:
                white_key_starts.append(white_key_starts[-1] + white_key_width + space_after)
            else:
                white_key_starts.append(0.0)
        else:
            black_key_offset = black_key_offsets[black_key_pitchclasses.index(key_pitchclass)]
            black_key_starts.append(white_key_starts[-1] + black_key_offset)

    width = white_key_starts[-1] + white_key_width
    height = white_key_height + red_velvet_height

    scale = white_key_width_px / white_key_width

    image = numpy.zeros((math.ceil(scale * height), math.ceil(scale * width), 3), numpy.uint8)
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
            border_color=(128, 128, 128),
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
            border_color=(128, 128, 128),
            border_thickness=1,
        )

    return image


if __name__ == "__main__":
    cv2.imshow("88-key piano", get_piano(50))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
