import argparse
import contextlib

import budgetpiano.ui

import cv2
import mido
import numpy


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


def find_segments(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, white_key_threshold = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Find contours in the image
    contours, _ = cv2.findContours(white_key_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours by area and select the largest ones as the piano keys
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    # Find the median area of the selected contours
    areas = [cv2.contourArea(c) for c in sorted_contours]
    median_area = numpy.median(areas)

    # Select the contours whose area is within a certain range of the median
    selected_contours = [c for c in sorted_contours if median_area * 0.5 <= cv2.contourArea(c) <= median_area * 1.5]

    # Create the source and destination points for the homography
    points = numpy.array([c for c in selected_contours], dtype=numpy.float32)
    dest = numpy.array([[i * 30, j * 30] for i in range(88) for j in range(2)], dtype=numpy.float32)

    # Find the homography matrix and warp the image
    if len(selected_contours) >= 4:
        h, _ = cv2.findHomography(points, dest)
        warped = cv2.warpPerspective(gray, h, (880, 60))

        cv2.imshow("warped", warped)
        cv2.waitKey(0)

        return warped, h

    return None, None


def main(video_source, midi_port):
    with video_capture(video_source) as cap:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            polygon = budgetpiano.ui.get_polygon(frame, "Select Piano polygon.")
            pass

            segments = find_segments(frame)

            # detect hand in frame ?

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
