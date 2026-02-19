import os
import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QInputDialog, QVBoxLayout, QWidget, QLineEdit
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

WINDOW_WIDTH = 450
WINDOW_HEIGHT = 350
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"

server_address_geocode = 'https://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'

app = QApplication(sys.argv)

class YandexMap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)

        address, ok = QInputDialog.getText(None, "Ввод", "Введите адрес:")
        if not ok:
            sys.exit()

        self.coordinates = self.get_coordinates(address)
        self.zoom = 0.002
        self.theme = "light"
        self.get_response()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.find_label = QLineEdit()
        self.layout.addWidget(self.find_label)

        self.image()


    def image(self):
        pixmap = QPixmap(MAP_FILE)
        self.resize(pixmap.width(), pixmap.height())
        self.image_label.setPixmap(pixmap)

        self.layout.addWidget(self.image_label)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_PageUp:
            self.zoom /= 2 if self.zoom > 0.0005 else 1
            self.get_response()
            self.image()
        if e.key() == Qt.Key.Key_PageDown:
            self.zoom *= 2 if self.zoom < 1 else 1
            self.get_response()
            self.image()

        step = self.zoom * 0.5
        lon = float(self.coordinates[0])
        lat = float(self.coordinates[1])

        if e.key() == Qt.Key.Key_W:
            if lat < 90:
                lat += step
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_S:
            if lat > -90:
                lat -= step
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_A:
            if lon > -180:
                lon -= step
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_D:
            if lon < 180:
                lon += step
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_Q:
            if self.theme == "light":
                self.theme = "dark"
            else:
                self.theme = "light"
            self.get_response()
            self.image()
        elif e.key() == Qt.Key.Key_Return:
            self.coordinates = self.get_coordinates(self.find_label.text())
            self.get_response()
            self.image()

    def get_response(self):
        server_address_static_map = 'https://static-maps.yandex.ru/v1?  '
        api_key_static_map = '2ac33b20-348f-4429-86d1-1ab126c72677'

        params_static_map = {
            "apikey": api_key_static_map,
            "ll": f"{self.coordinates[0]},{self.coordinates[1]}",
            "spn": f"{self.zoom},{self.zoom}",
            "size": "400,300",
            "theme": self.theme,
            "pt": self.pt
        }

        response = requests.request("GET", server_address_static_map, params=params_static_map)

        with open(MAP_FILE, "wb") as file:
            file.write(response.content)

    def get_coordinates(self, address):
        params_geocode = {
            "apikey": api_key_geocode,
            "geocode": address,
            "format": "json"
        }

        response = requests.request("GET", server_address_geocode, params=params_geocode).json()

        coordinates = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            "pos"].split()

        self.pt = f"{coordinates[0]},{coordinates[1]},pm2dgl"

        return coordinates


def main():
    window = YandexMap()
    window.show()
    app.exec()
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()