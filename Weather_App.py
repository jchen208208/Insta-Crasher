import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt #used for alignment

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.button = QPushButton("Retrieve Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji = QLabel(self)
        self.description = QLabel(self)
        self.setFixedSize(400, 600)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addSpacing(20)
        vbox.addWidget(self.button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji)
        vbox.addWidget(self.description)
        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.button.setObjectName("button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji.setObjectName("emoji")
        self.description.setObjectName("description")

        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit{
                font-family: Times New Roman;
                border-radius: 10px;
            }
            QLabel#city_label{
                font-style: italic;
                font-size: 40px;
            }
            QLineEdit#city_input{
                font-size: 40px;
            }
            QPushButton#button{
                font-size: 30px;
                font-weight: bold;
                border: 3px solid;
                border-color: white;
                background-color: #1a1a1a;
            }
            QPushButton:hover{
                background-color: #333333;
            }
            QPushButton:pressed{
                background-color: #111111; /* Darkens slightly when clicked */
                padding-top: 5px;          /* This creates the "sinking" effect */
                border-style: inset;       /* Changes the border look to seem pushed in */
            }
            QLabel#temperature_label{
                font-size: 75px;
                font-weight: bold;
            }
            QLabel#emoji{
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
            QLabel#description{
                font-size: 50px;
            }
        """)

        self.button.clicked.connect(self.getWeather)


    def getWeather(self):
        api_key = "89e003e3065a1eb33279f4182e1040d3"
        city = self.city_input.text().lower()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.display_weather(data)
            self.displayEmoji(weather)


        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                self.description.setText("City Not Found")
            else:
                self.description.setText(f"HTTP Error: {response.status_code}")
            self.temperature_label.hide()
            self.emoji.hide()
        except requests.exceptions.RequestException:
            self.description.setText("Connection Error")

    weather = ""

    def display_weather(self, data):
        if data["cod"] != "404":
            global weather
            self.temperature_label.show()
            self.emoji.show()
            temp_k = data['main']['temp']
            temp_c = temp_k - 273.15
            weather = data['weather'][0]['main']
            self.temperature_label.setText(f"{temp_c:.1f}ºC")
            self.description.setText(weather)

    def displayEmoji(self, weather):
        emoji_map = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️"
        }

        self.emoji.setText(emoji_map[weather])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())