# Shree KRISHNAya Namaha
# GUI for emotion recognition
# Emojis link: https://emojiisland.com/pages/download-new-emoji-icons-in-png-ios-10
# Authors: Nagabhushan S N, Sandesh Rao M
# Last Modified: 27-02-2020

import platform
import tkinter
import tkinter.ttk
from enum import Enum
import random
import cv2

import PIL
import PIL.Image
import PIL.ImageTk
import skimage.io
import skimage.transform
import skimage.color
import time
import vlc

import EmotionDetector

from custom.Fonts.TimesNewRoman import TimesNewRoman
import numpy

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
GAME_DURATION = 60
EMOTION_TIME_LIMIT = 20
LOGO_WIDTH = 100
LOGO_HEIGHT = 100


class Emotions(Enum):
    ANGRY = 'Angry'
    DISGUST = 'Disgust'
    SCARED = 'Scared'
    HAPPY = 'Happy'
    SAD = 'Sad'
    SURPRISED = 'Surprised'
    NEUTRAL = 'Neutral'


class StartScreen:
    def __init__(self, window):
        self.window = window
        self.start_button = None
        self.start_time = -1

    def build(self):
        self.start_button = tkinter.Button(self.window, text='Start', command=self.start_game)
        self.start_button.place(relx=0.5, rely=0.5)

    def start_game(self):
        # self.start_button.place_forget()
        self.start_time = time.time()
        # while time.time() - self.start_time < 30:
        game_screen = GameScreen(self.window)
        game_screen.build()
        print('Hello')
        return


class GameScreen:
    def __init__(self, window):
        self.window = window
        self.iisc_canvas = None
        self.iisc_logo = None
        self.ece_canvas = None
        self.ece_logo = None
        self.start_button = None
        self.big_title = None
        self.title_label = None
        self.counter_label = None
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, 640)
        self.camera.set(4, 480)
        self.user_canvas = None
        self.user_image = None
        self.smiley_canvas = None
        self.smiley_image = None
        self.smiley_label = None
        self.timer_progress = None
        self.timer_label = None
        self.score_label = None
        self.time_remaining = GAME_DURATION
        self.after_emotion_id = None
        self.after_refresh_id = None
        self.after_timer_id = None
        self.after_refresh2_id = None
        self.all_target_emotions = None
        self.target_emotion = None
        self.correct_counter = 0
        self.try_counter = 0
        self.current_emotion_start_time = -1

    def build(self):
        self.start_button = tkinter.Button(self.window, text='Start', command=self.start_game,
                                           font=TimesNewRoman().header1)
        self.start_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.iisc_canvas = tkinter.Canvas(self.window, height=LOGO_HEIGHT, width=LOGO_WIDTH, bg='white', highlightthickness=0)
        iisc_image = skimage.io.imread('../res/images/iisc_emblem.png')
        iisc_image = skimage.color.rgba2rgb(iisc_image)
        iisc_image = (skimage.transform.resize(iisc_image, (LOGO_HEIGHT-10, LOGO_WIDTH-10)) * 255).astype('uint8')
        self.iisc_logo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(iisc_image))
        self.iisc_canvas.create_image(LOGO_WIDTH//2, LOGO_HEIGHT//2, image=self.iisc_logo, anchor=tkinter.CENTER)
        self.iisc_canvas.place(relx=0.15, rely=0.1, anchor=tkinter.CENTER)

        self.ece_canvas = tkinter.Canvas(self.window, height=LOGO_HEIGHT, width=LOGO_WIDTH*3, bg='white', highlightthickness=0)
        ece_image = skimage.io.imread('../res/images/ece_logo.png')
        # ece_image = skimage.color.rgba2rgb(ece_image)
        ece_image = (skimage.transform.resize(ece_image, (LOGO_HEIGHT, LOGO_WIDTH*2)) * 255).astype('uint8')
        self.ece_logo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(ece_image))
        self.ece_canvas.create_image(LOGO_WIDTH//2, LOGO_HEIGHT//2, image=self.ece_logo, anchor=tkinter.W)
        self.ece_canvas.place(relx=0.8, rely=0.1, anchor=tkinter.CENTER)

        self.big_title = tkinter.Label(text='Wait...', bg='white', font=TimesNewRoman().header1)
        self.title_label = tkinter.Label(text='Wait...', bg='white', font=TimesNewRoman().text1)
        self.counter_label = tkinter.Label(text='Wait...', bg='white', font=TimesNewRoman().text1)
        self.score_label = tkinter.Label(text='', bg='white', font=TimesNewRoman().header1)

        self.user_canvas = tkinter.Canvas(self.window, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bg='white')
        self.smiley_canvas = tkinter.Canvas(self.window, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bg='white', highlightthickness=0)
        self.smiley_label = tkinter.Label(self.window, text='', bg='white', font=TimesNewRoman().text1)

        self.timer_progress = tkinter.ttk.Progressbar(self.window, orient= tkinter.HORIZONTAL, length=1000, mode='determinate')
        # self.timer_progress.place(relx=0.5, rely=0.95, anchor=tkinter.CENTER)
        # self.timer_label = tkinter.Label(text='01:00', bg='white', font=TimesNewRoman().text1)
        # self.timer_label.place(relx=0.5, rely=0.95, anchor=tkinter.CENTER)

    def start_game(self):
        self.try_counter = 0
        self.correct_counter = 0
        self.update_counter_label()
        self.all_target_emotions = self.draw_target_emotions()
        self.time_remaining = GAME_DURATION
        self.start_button.place_forget()
        self.score_label.place_forget()
        self.refresh()
        self.update_timer()
        return

    @staticmethod
    def draw_target_emotions():
        a = numpy.arange(7)
        numpy.random.shuffle(a)
        target_emotions = a[:5]
        target_emotions = numpy.array(list(target_emotions) + [3, 6])
        numpy.random.shuffle(target_emotions)
        random_emotions = numpy.random.randint(0, 7, 23)
        all_target_emotions = numpy.concatenate([target_emotions, random_emotions])
        return all_target_emotions

    def refresh(self):
        self.target_emotion = list(Emotions)[self.all_target_emotions[self.try_counter]]
        self.try_counter = (self.try_counter + 1) % 30
        inst = f'Show me your {self.target_emotion.name} face'
        self.big_title.config(text=inst)
        self.title_label.config(text=inst)
        self.big_title.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.title_label.place_forget()
        self.counter_label.place_forget()
        self.user_canvas.place_forget()
        self.smiley_canvas.place_forget()
        self.smiley_label.place_forget()
        self.timer_progress.place(relx=0.5, rely=0.95, anchor=tkinter.CENTER)
        self.after_refresh2_id = self.window.after(1000, self.refresh2)
        self.current_emotion_start_time = time.time()

    def refresh2(self):
        self.big_title.place_forget()
        self.title_label.place(relx=0.5, rely=0.05, anchor=tkinter.CENTER)
        self.counter_label.place(relx=0.5, rely=0.10, anchor=tkinter.CENTER)
        self.user_canvas.place(relx=0.25, rely=0.5, anchor=tkinter.CENTER)
        self.smiley_canvas.place(relx=0.75, rely=0.5, anchor=tkinter.CENTER)
        self.smiley_label.place(relx=0.75, rely=0.8, anchor=tkinter.CENTER)
        self.update_emotion()

    def update_emotion(self):
        frame = self.camera.read()[1]
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # tmp = [0, 2, 3, 3, 2, 0, 0, 2, 3, 2, 1]
        # random_emotion = tmp[random.randint(0, 10)]
        # detected_emotion = list(Emotions)[random_emotion]
        detected_emotion = EmotionDetector.detect_emotion(rgb_image)
        emotion_path = f'../res/images/smileys/{detected_emotion.value}.png'
        emotion_image = skimage.io.imread(emotion_path)
        emotion_image = skimage.color.rgba2rgb(emotion_image)
        resized_image = (skimage.transform.resize(emotion_image, (CANVAS_HEIGHT-20, CANVAS_WIDTH-20)) * 255).astype('uint8')
        self.user_image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(rgb_image))
        self.user_canvas.create_image(CANVAS_WIDTH//2, CANVAS_HEIGHT//2, image=self.user_image, anchor=tkinter.CENTER)
        self.smiley_image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(resized_image))
        self.smiley_canvas.create_image(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, image=self.smiley_image,
                                        anchor=tkinter.CENTER)
        self.smiley_label.config(text=detected_emotion.value)
        if detected_emotion.value != self.target_emotion.value:
            if time.time() - self.current_emotion_start_time <= EMOTION_TIME_LIMIT:
                self.after_emotion_id = self.window.after(250, self.update_emotion)
            else:
                # Time expired for current emotion
                self.after_refresh_id = self.window.after(1000, self.refresh)
        else:
            self.correct_counter += 1
            self.update_counter_label()
            p = vlc.MediaPlayer('../res/audios/Success.mp3')
            p.play()
            self.after_refresh_id = self.window.after(1000, self.refresh)
        return

    def update_timer(self):
        self.time_remaining -= 1
        # self.timer_label.config(text=f'00:{self.time_remaining:02}')
        self.timer_progress['value'] = (self.time_remaining * 100 / 60)
        if self.time_remaining == 0:
            self.end_current_trial()
        else:
            self.after_timer_id = self.window.after(1000, self.update_timer)

    def end_current_trial(self):
        self.cancel_after_ids(
            [self.after_emotion_id, self.after_refresh_id, self.after_timer_id, self.after_refresh2_id])
        self.big_title.place_forget()
        self.title_label.place_forget()
        self.counter_label.place_forget()
        self.user_canvas.place_forget()
        self.smiley_canvas.place_forget()
        self.smiley_label.place_forget()
        self.score_label.config(text=f'Your score is {self.correct_counter}')
        self.score_label.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
        self.start_button.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
        # self.timer_label.config(text='01:00')
        self.timer_progress.place_forget()

    def cancel_after_ids(self, id_list: list):
        for id in id_list:
            if id:
                self.window.after_cancel(id)

    def update_counter_label(self):
        self.counter_label.config(text=f'Points: {self.correct_counter}')


def start_window():
    root_window = tkinter.Tk()
    root_window.option_add('*Dialog.msg.font', 'Times 12')
    root_window.configure(background='white')
    if platform.system() == 'Windows':
        # root_window.state('zoomed')
        root_window.attributes('-fullscreen', True)
    elif platform.system() == 'Linux':
        root_window.attributes('-zoomed', True)

    start_screen = GameScreen(root_window)
    start_screen.build()
    root_window.mainloop()
    return


def main():
    start_window()


if __name__ == '__main__':
    main()
