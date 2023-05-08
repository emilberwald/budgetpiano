import mido
import tkinter
import tkinter.simpledialog


class MidiPortPicker(tkinter.simpledialog.Dialog):
    def __init__(self, parent=None):
        if parent is None:
            self.parent = tkinter.Tk()
            self.parent.withdraw()

        self.output_names = mido.get_output_names()

        super().__init__(parent=self.parent, title="Select Midi Output Port")

    def body(self, root):
        root.title("Select MIDI Output Port")

        self.frame = tkinter.Frame(root)
        self.frame.pack()

        self.label = tkinter.Label(self.frame, text="Select MIDI output port:")
        self.label.pack()

        self.listbox = tkinter.Listbox(self.frame, width=50)
        self.listbox.pack()

        for name in self.output_names:
            self.listbox.insert(tkinter.END, name)

    def apply(self):
        self.result = self.listbox.get(tkinter.ACTIVE)


def ask_for_midi_port():
    return MidiPortPicker().result
