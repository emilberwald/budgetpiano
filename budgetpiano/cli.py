import argparse
import contextlib
import itertools

import budgetpiano.gui
import budgetpiano.matcher

import cv2
import mido
import numpy
import scipy, scipy.optimize

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
    for template_corners in list(itertools.permutations(template_pts)):
        H, _ = cv2.findHomography(img_pts, numpy.asarray(template_corners))
        warped_img = cv2.warpPerspective(img, H, (template.shape[1], template.shape[0]))
        l2_distance = cv2.norm(warped_img, template)
        if (smallest is None) or (l2_distance < smallest):
            smallest = l2_distance
            homography = H
        else:
            pass
    return homography


def find_homography_manual(img, template, img_pts):
    template_pts = get_corners(template)
    homography = None
    for template_corners in list(itertools.permutations(template_pts)):
        H, _ = cv2.findHomography(img_pts, numpy.asarray(template_corners))
        warped_img = cv2.warpPerspective(img, H, (template.shape[1], template.shape[0]))
        if budgetpiano.gui.ask_image_question(warped_img):
            return homography
    raise ValueError("No template match good enough")


def cost_function(params, *args):
    homography = params.reshape((3, 3))
    source = args[0]
    cost = 0.0
    for template in args[1:]:
        destination = cv2.warpPerspective(source, homography, (template.shape[1], template.shape[0]))
        cost += numpy.linalg.norm(destination.astype(float) - template.astype(float))
    return cost


def main(video_source, midi_port):
    instrument_template = None
    while instrument_template is None:
        instrument_template = budgetpiano.gui.ask_for_piano_image()
    instrument_templates = [instrument_template]
    instrument_homography = None

    with video_capture(video_source) as cap:
        target_fps = 2.0
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_skip = round(video_fps / target_fps)

        nof_history_frames = int(cap.get(cv2.CAP_PROP_FPS) * 10.0)
        with managed_resource(
            cv2.createBackgroundSubtractorMOG2(history=nof_history_frames, detectShadows=False)
        ) as bg_model:
            while cap.isOpened():
                if cap.grab():
                    frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    if frame_no % frame_skip != 0:
                        continue
                else:
                    break
                ret, frame = cap.read()
                if not ret:
                    break

                if instrument_homography is None:
                    manual_polygon = budgetpiano.gui.ask_for_polygon(frame, "Select Piano polygon.")
                    manual_homography = find_homography(frame, instrument_template, manual_polygon)
                    manual_instrument = cv2.warpPerspective(
                        frame, manual_homography, (instrument_template.shape[1], instrument_template.shape[0])
                    )
                    instrument_templates.append(manual_instrument)
                    instrument_homography = manual_homography

                result = scipy.optimize.minimize(
                    cost_function, instrument_homography.ravel(), args=(frame, *instrument_templates)
                )
                instrument_homography = result.x.reshape((3, 3))
                instrument_image = cv2.warpPerspective(
                    frame, instrument_homography, (instrument_template.shape[1], instrument_template.shape[0])
                )

                # detect fingers

                foreground = bg_model.apply(instrument_image)
                background = bg_model.getBackgroundImage()
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
