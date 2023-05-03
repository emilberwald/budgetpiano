import copy

import numpy
import cv2
import tkinter
import mido


def get_midi_port():
    root = tkinter.Tk()
    root.title("Select MIDI Output Port")
    selected_port = tkinter.StringVar()

    def set_port(event=None):
        selected_port.set(listbox.get(tkinter.ACTIVE))
        root.destroy()

    frame = tkinter.Frame(root)
    frame.pack(padx=10, pady=10)

    label = tkinter.Label(frame, text="Select MIDI output port:")
    label.pack()

    listbox = tkinter.Listbox(frame, width=50)
    listbox.pack(pady=10)

    for name in mido.get_output_names():
        listbox.insert(tkinter.END, name)

    button_ok = tkinter.Button(frame, text="OK", command=set_port)
    button_ok.pack(pady=10)

    root.bind("<Return>", set_port)
    root.bind("<Escape>", lambda event: root.destroy())

    # Use mainloop to run the GUI and wait for the user to select a port
    root.mainloop()

    return selected_port.get()


def get_polygon(image: numpy.ndarray, window_title="Select a Polygon"):
    def _mouse_callback(event, x, y, flags, params):
        params["point"] = (x, y)

        if flags & cv2.EVENT_FLAG_CTRLKEY:
            params["is_deleting"] = True
            params["is_selecting"] = False
            if event == cv2.EVENT_LBUTTONUP:
                params["points"].pop() if params["points"] else None
        else:
            if event == cv2.EVENT_LBUTTONDOWN:
                params["is_selecting"] = True
                return
            elif event == cv2.EVENT_LBUTTONUP:
                params["is_selecting"] = False
                if not (x, y) in params["points"]:
                    params["points"].append((x, y))
                return
            elif event == cv2.EVENT_RBUTTONUP and len(params["points"]) >= 3:
                params["is_finished"] = True
                return

    try:
        params = {"is_deleting": False, "is_selecting": False, "is_finished": False, "points": [], "point": [0, 0]}
        window_name = "PolygonSelector"
        cv2.namedWindow(window_name)
        cv2.setWindowTitle(window_name, window_title)
        cv2.setMouseCallback(window_name, _mouse_callback, params)
        cv2.imshow(window_name, image)
        while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:

            image_with_overlay = image.copy()
            color = (0, 255, 0)
            line_points = copy.deepcopy(params["points"])
            if params["is_selecting"]:
                cv2.drawMarker(image_with_overlay, params["point"], color, cv2.MARKER_CROSS, 10, 2)
                line_points.append(params["point"])

            if len(line_points) < 3:
                cv2.polylines(image_with_overlay, [numpy.asarray(line_points, numpy.int32)], True, color, 2)
            else:
                polygon_overlay = image.copy()
                cv2.fillPoly(polygon_overlay, [numpy.asarray(line_points, numpy.int32)], color)
                opacity = 0.5
                image_with_overlay = cv2.addWeighted(polygon_overlay, opacity, image_with_overlay, 1 - opacity, 0)

            cv2.imshow(window_name, image_with_overlay)
            cv2.waitKey(1)
            if params["is_finished"]:
                return [p for p in params["points"]]
    finally:
        cv2.destroyAllWindows()
