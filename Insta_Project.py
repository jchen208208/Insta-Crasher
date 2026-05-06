import sys
import pygame
import string
import time
import threading
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

driver = None
was_on_instagram = False

class Timer(QWidget):
    start_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen.width(), screen.top(), 200, 50)
        self.setFixedSize(300, 100)
        self.timeLabel = QLabel(self)
        self.timer = QTimer(self)
        self.remaining_seconds = 10
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Timer of Doom")

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.timeLabel)
        self.setLayout(vbox)
        self.timeLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeLabel.setStyleSheet("background-color: black;"
                                     "color: white;")
        font_id = QFontDatabase.addApplicationFont("/Users/botboy/Downloads/DS-DIGIT.TTF")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.timeLabel.setFont(QFont(font_family, 100))
        self.setStyleSheet("background-color: black;")

        self.timer.timeout.connect(self.update_time)

    def start_timer(self):  # ← add this method
        self.show()
        self.update_time()

    def check_instagram(self):
        try:
            response = requests.get("http://localhost:9222/json")
            tabs = response.json()
            page_tabs = [tab for tab in tabs if tab.get("type") == "page"]
            
            on_instagram = False
            insta_exists = False
            
            for tab in tabs:
                if "instagram.com" in tab.get("url", ""):
                    insta_exists = True
                    break
            
            if page_tabs:
                active_url = page_tabs[0].get("url", "")
                if "instagram.com" in active_url:
                    on_instagram = True
            
            return on_instagram, insta_exists

        except Exception:
            return False, False

    def update_time(self):
        global driver
        global was_on_instagram

        if self.remaining_seconds >= 0:
            on_instagram, insta_exists = self.check_instagram()
            
            if not on_instagram:
                if was_on_instagram and not insta_exists:
                    self.timer.stop()
                    self.hide()
                    self.remaining_seconds = 10
                    display2.show()
                    display2.show_vid()
                    display2.your_next_channel = display2.play_sound(display2.your_next, False)
                    was_on_instagram = False
                    return
                else:
                    self.timer.stop()
                    self.hide()
                    return

            was_on_instagram = True
            mins = self.remaining_seconds // 60
            secs = self.remaining_seconds % 60
            self.timeLabel.setText(f"{mins:02d}:{secs:02d}")
            self.remaining_seconds -= 1
            self.timer.start(1000)


        else:

            self.timer.stop()
            self.timeLabel.setStyleSheet("color: red; background-color: black;")
            self.hide()

            on_instagram, _ = self.check_instagram()

            if on_instagram:

                try:
                    response = requests.get("http://localhost:9222/json")
                    tabs = response.json()

                    for tab in tabs:
                        if "instagram.com" in tab.get("url", ""):
                            driver.switch_to.window(tab["id"])
                            driver.close()
                            break

                except Exception as e:
                    print(f"Error closing tab: {e}")

                display.show()
                display.play_sound(display.freddy_sound)
                display.play_sound(display.static_sound)
                display.start_typing()

            else:

                display2.show()
                display2.your_next_channel = display2.play_sound(display2.your_next, False)
                display2.show_vid()


class Display(QWidget):
    def __init__(self):
        super().__init__()
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry((self.screen.width() - self.width()) // 2, (self.screen.height() - self.height()) // 2, 700, 550)
        self.freddy_sound = pygame.mixer.Sound("/Users/botboy/PyCharmMiscProject/Insta_Proiect/[Nightmare Freddy]Stop ......live..mp3")
        self.static_sound = pygame.mixer.Sound("/Users/botboy/PyCharmMiscProject/Insta_Proiect/Static.mp3")
        self.check_time = QTimer(self)
        self.label = QLabel("")
        self.label.setGeometry(0, 0, 100, 50)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.full_text = "Stop doomscrolling. Now! Get back to work! If you wanna live!"
        self.current_index = 0
        self.typing_timer = QTimer(self)
        self.clear_next = False
        self.image = QLabel(self)

        self.initUI()
        self.hide()

    def initUI(self):
        self.setWindowTitle("Boo!")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        font_id = QFontDatabase.addApplicationFont("/Users/botboy/Downloads/HorrorFont-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.label.setFont(QFont(font_family, 300))
        self.label.setStyleSheet("font-size: 50px; color: red;")
        self.label.setWordWrap(True)
        self.image.setGeometry(0, 0, 0, 0)
        self.image.setFixedSize(700, 550)
        image_map = QPixmap("/Users/botboy/PyCharmMiscProject/Insta_Proiect/Nightmareattack.webp")
        self.image.setPixmap(image_map)
        self.image.setScaledContents(True)
        self.image.show()
        self.image.lower()


    def play_sound(self, sound, loop = False):
        return sound.play(loops = 3 if loop else 0)

    def stop_static(self):
        if not self.freddy_channel.get_busy():
            self.static_channel.stop()
            self.check_time.stop()

    def start_typing(self):
        self.current_index = 0
        self.label.setText("")
        self.typing_timer.timeout.connect(self.add_next_character)
        self.typing_timer.start(50)


    def add_next_character(self):
        chars = string.punctuation
        if self.current_index >= len(self.full_text):
            self.typing_timer.stop()
            return

        if self.clear_next:
            self.label.setText("")
            self.clear_next = False

        elif self.current_index < len(self.full_text):
            current_display = self.label.text()
            self.label.setText(current_display + self.full_text[self.current_index])
            if self.full_text[self.current_index] in chars:
                self.typing_timer.setInterval(600)
                self.clear_next = True
            else:
                self.typing_timer.setInterval(50)
            self.current_index += 1


class Display2(Display):
    def __init__(self):
        QWidget.__init__(self)
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.your_next = pygame.mixer.Sound("/Users/botboy/PyCharmMiscProject/Insta_Proiect/congratulations.mp3")
        self.setGeometry((self.screen.width() - self.width()) // 2, (self.screen.height() - self.height()) // 2, 700, 550)
        self.check_time = QTimer(self)
        self.image = QLabel(self)
        self.video = QVideoWidget(self)
        self.video.setFixedSize(700, 550)
        self.video.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        self.video.hide()
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video)
        self.player.setSource(QUrl.fromLocalFile("/Users/botboy/PyCharmMiscProject/Insta_Proiect/Congrats.mp4"))
        self.label = QLabel("Congratulations", self)
        self.label.setGeometry(0, 0, 700, 100)

        self.initUI()
        self.hide()

    def initUI(self):
        self.setWindowTitle("Congratulations!")
        font_id = QFontDatabase.addApplicationFont("/Users/botboy/Downloads/HorrorFont-Regular.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.label.setFont(QFont(font_family, 30))
        self.label.setStyleSheet("font-size: 30px; color: red;")
        self.label.setWordWrap(True)
        self.image.setGeometry(0, 0, 0, 0)
        self.image.setFixedSize(700, 550)
        image_map = QPixmap("/Users/botboy/PyCharmMiscProject/Insta_Proiect/might.jpeg")
        self.image.setPixmap(image_map)
        self.image.setScaledContents(True)
        self.image.hide()
        self.image.lower()


    def show_vid(self):
        self.video.show()
        self.video.lower()
        self.label.raise_()
        self.player.play()

def sel():
    global driver
    options = Options()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    was_on_instagram = False

    while True:
        try:
            response = requests.get("http://localhost:9222/json")
            tabs = response.json()
            page_tabs = [tab for tab in tabs if tab.get("type") == "page"]
            
            on_instagram = False
            if page_tabs:
                active_url = page_tabs[0].get("url", "")
                if "instagram.com" in active_url:
                    on_instagram = True
            
            if on_instagram and not was_on_instagram:
                timer.start_signal.emit()
                was_on_instagram = True
            elif not on_instagram:
                was_on_instagram = False
                
        except Exception:
            pass
        time.sleep(2)


if __name__ == "__main__":
    app1 = QApplication(sys.argv)
    timer = Timer()
    pygame.mixer.init()
    display = Display()
    display2 = Display2()

    timer.start_signal.connect(timer.start_timer)

    thread = threading.Thread(target=sel, daemon=True)
    thread.start()

    sys.exit(app1.exec())


