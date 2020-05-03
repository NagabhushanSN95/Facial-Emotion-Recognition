# Shree KRISHNAya Namaha
# Times New Roman font in different sizes
# Author: Nagabhushan S N
# Last Modified: 08/09/2019

from tkinter.font import Font


class TimesNewRoman:
    # FIXME: Make this class Singleton
    def __init__(self) -> None:
        self.header1 = Font(family='Times New Roman', size=30)
        self.header2 = Font(family='Times New Roman', size=25)
        self.header3 = Font(family='Times New Roman', size=20)
        self.text1 = Font(family='Times New Roman', size=18)
        self.text2 = Font(family='Times New Roman', size=15)
        self.text3 = Font(family='Times New Roman', size=12)
