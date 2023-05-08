import argparse
import contextlib

import budgetpiano.gui
import budgetpiano.matcher

import cv2
import mido
import numpy

import contextlib


@contextlib.contextmanager
def managed_resource(resource):
    try:
        yield resource
    finally:
        del resource


@contextlib.contextmanager
def open_midi_port(port_name):
    with mido.open_output(port_name) as port:
        yield port


@contextlib.contextmanager
def video_capture(video_source):
    cap = cv2.VideoCapture(video_source)
    try:
        yield cap
    finally:
        cap.release()


def get_corners(image):
    height, width = image.shape[:2]
    corners = [[0, 0], [width, 0], [width, height], [0, height]]
    return corners


def find_homography(img, template, img_pts):
    template_pts = get_corners(template)
    smallest = None
    homography = None
    for i in range(len(template_pts)):
        template_corners = numpy.roll(template_pts, i, axis=0)
        H, _ = cv2.findHomography(img_pts, numpy.asarray(template_corners))
        warped_img = cv2.warpPerspective(img, H, (template.shape[1], template.shape[0]))
        l2_distance = cv2.norm(warped_img, template)
        if (smallest is None) or (l2_distance < smallest):
            smallest = l2_distance
            homography = H
        else:
            pass
    return homography


def main(video_source, midi_port):
    instrument_homography = None

    with video_capture(video_source) as cap:
        matcher = budgetpiano.matcher.GrayscaleMatcher()

        nof_history_frames = int(cap.get(cv2.CAP_PROP_FPS) * 0.1)
        with managed_resource(
            cv2.createBackgroundSubtractorMOG2(history=nof_history_frames, detectShadows=False)
        ) as bg_model:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                stabilized_homography = matcher.get_homography(gray)
                if stabilized_homography is not None:
                    stabilized_frame = cv2.warpPerspective(
                        frame, stabilized_homography, (frame.shape[1], frame.shape[0])
                    )
                    if instrument_homography is None:
                        polygon = budgetpiano.gui.ask_for_polygon(frame, "Select Piano polygon.")
                        piano = budgetpiano.gui.ask_for_piano_image()
                        instrument_homography = find_homography(stabilized_frame, piano, polygon)

                    instrument_image = cv2.warpPerspective(
                        stabilized_frame, instrument_homography, (piano.shape[1], piano.shape[0])
                    )
                    #detect fingers

                    instrument_gray = cv2.cvtColor(instrument_image, cv2.COLOR_BGR2GRAY)
                    foreground = bg_model.apply(instrument_gray)
                    pass

                    # if finger points at key of piano, send midi event
                    if midi_port:
                        with open_midi_port(midi_port) as port:
                            port.send(mido.Message("note_on", note=60, velocity=64))
                            port.send(mido.Message("note_off", note=60))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--video-source", type=str, help="Inumpyut source for video capture")
    args = parser.parse_args()
    # midi_port = get_midi_port()
    midi_port = None
    main(args.video_source, midi_port)
