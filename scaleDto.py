from tkinter import Text, WORD


class ScaleDto:

    def __init__(self, frame=None):
        self.var = 0
        self.text = Text(frame, width=25, height=5, bg="darkgreen", fg='white', wrap=WORD)
        self.text.pack()

    def on_scale(self, val):
        self.var = int(float(val))
        self.text.insert(1.0, str(self.var))
