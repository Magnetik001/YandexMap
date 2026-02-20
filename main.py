import math
import os
import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QInputDialog, QVBoxLayout, QWidget, QLineEdit, \
    QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

WINDOW_WIDTH = 550
WINDOW_HEIGHT = 550
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"

app = QApplication(sys.argv)

class YandexMap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)

        address, ok = QInputDialog.getText(None, "Ввод", "Введите адрес:")
        if not ok:
            sys.exit()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        self.find_line = QLineEdit()
        self.find_line.textChanged.connect(self.find)
        self.layout.addWidget(self.find_line)

        self.info_label = QLabel()
        self.layout.addWidget(self.info_label)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset)
        self.layout.addWidget(self.reset_button)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.layout.addWidget(self.image_label)

        self.zoom = 17

        self.theme = "light"
        self.postal_code = False
        self.block_finder = True

        self.get_coordinates(address)
        self.find_line.blockSignals(self.block_finder)

        self.get_response()
        self.image()

    def image(self):
        pixmap = QPixmap(MAP_FILE)
        self.resize(pixmap.width(), pixmap.height())
        self.image_label.setPixmap(pixmap)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_PageUp:
            if self.zoom < 21:
                self.zoom += 1
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_PageDown:
            if self.zoom > 0:
                self.zoom -= 1
                self.get_response()
                self.image()

        pix_w = 450
        lon_span = 360 * pix_w / (256 * 2 ** self.zoom)
        lat_span = lon_span * math.cos(math.radians(float(self.coordinates[1])))

        step_lat = lat_span * 0.5
        step_lon = lon_span * 0.5

        lon = float(self.coordinates[0])
        lat = float(self.coordinates[1])

        if e.key() == Qt.Key.Key_W:
            if lat < 85:
                lat += step_lat
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_S:
            if lat > -85:
                lat -= step_lat
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_A:
            if lon > -180:
                lon -= step_lon
                self.coordinates = [str(lon), str(lat)]
                self.get_response()
                self.image()
        elif e.key() == Qt.Key.Key_D:
            if lon < 180:
                lon += step_lon
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
        elif e.key() == Qt.Key.Key_E:
            self.postal_code = not self.postal_code
            if self.postal_code:
                self.info_label.setText(f"{self.info2} {self.info1}")
            else:
                self.info_label.setText(f"{self.info1}")
        elif e.key() == Qt.Key.Key_Z:
            self.block_finder = not self.block_finder
            self.find_line.blockSignals(self.block_finder)
        elif e.key() == Qt.Key.Key_Return:
            self.find()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pixmap = self.image_label.pixmap()
            if not pixmap:
                return

            pos = self.image_label.mapFromGlobal(event.globalPosition().toPoint())

            pix_w = pixmap.width()
            pix_h = pixmap.height()
            label_w = self.image_label.width()
            label_h = self.image_label.height()

            scale = min(label_w / pix_w, label_h / pix_h)
            real_w = pix_w * scale
            real_h = pix_h * scale
            offset_x = (label_w - real_w) / 2
            offset_y = (label_h - real_h) / 2

            real_x = (pos.x() - offset_x) / scale
            real_y = (pos.y() - offset_y) / scale

            if 0 <= real_x <= pix_w and 0 <= real_y <= pix_h:
                center_lon = float(self.coordinates[0])
                center_lat = float(self.coordinates[1])

                lon_span = 360 * pix_w / (256 * 2 ** self.zoom)

                lat_span = lon_span * math.cos(math.radians(center_lat))

                x_ratio = real_x / pix_w
                y_ratio = real_y / pix_h

                new_lon = center_lon + (x_ratio - 0.5) * lon_span
                new_lat = center_lat - (y_ratio - 0.5) * lat_span

                click_address = f"{new_lon},{new_lat}"
                self.get_coordinates(click_address, 2)
                self.get_response()
                self.image()
        elif event.button() == Qt.MouseButton.RightButton:
                search_api_server = "https://search-maps.yandex.ru/v1/"
                search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

                current_lon = float(self.coordinates[0])
                current_lat = float(self.coordinates[1])

                delta_lat = 100 / 111111
                delta_lon = 100 / (111111 * math.cos(math.radians(current_lat)))

                search_params = {
                    "apikey": search_api_key,
                    "text": self.find_line.text(),
                    "lang": "ru_RU",
                    "ll": f"{current_lon},{current_lat}",
                    "spn": f"{delta_lon},{delta_lat}",
                    "type": "biz",
                    "rspn": "1",
                    "results": "1"
                }

                response = requests.get(search_api_server, params=search_params)
                response_json = response.json()

                if len(response_json["features"]) > 0:
                    organization = response_json["features"][0]
                    point = organization["geometry"]["coordinates"]
                    org_name = organization["properties"]["CompanyMetaData"]["name"]
                    org_address = organization["properties"]["CompanyMetaData"]["address"]

                    self.coordinates = [str(point[0]), str(point[1])]

                    self.info1 = org_name
                    self.info2 = org_address
                    self.info_label.setText(f"{self.info1}")

                    self.pt = f"{self.coordinates[0]},{self.coordinates[1]},pm2dgl"

                    self.get_response()
                    self.image()
                else:
                    print("В радиусе 50 метров ничего не найдено")

    def get_response(self):
        server_address_static_map = 'https://static-maps.yandex.ru/v1?'
        api_key_static_map = '2ac33b20-348f-4429-86d1-1ab126c72677'

        params_static_map = {
            "apikey": api_key_static_map,
            "ll": f"{self.coordinates[0]},{self.coordinates[1]}",
            "z": str(self.zoom),
            "size": "450,450",
            "theme": self.theme,
            "pt": self.pt
        }

        response = requests.request("GET", server_address_static_map, params=params_static_map)

        if response.status_code == 200:
            with open(MAP_FILE, "wb") as file:
                file.write(response.content)
        else:
            print("Ошибка получения карты:", response.status_code)

    def get_coordinates(self, address, mode=1):
        server_address_geocode = 'https://geocode-maps.yandex.ru/1.x/?'
        api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'

        params_geocode = {
            "apikey": api_key_geocode,
            "geocode": address,
            "format": "json"
        }

        response1 = requests.request("GET", server_address_geocode, params=params_geocode)
        response = response1.json()

        if response1.status_code == 200 and len(response["response"]["GeoObjectCollection"]["featureMember"]) > 0:
            if mode == 1:
                self.coordinates = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                    "pos"].split()
            self.info1 = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["name"]
            try:
                self.info2 = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
            except KeyError:
                self.info2 = ""
            if mode == 1:
                self.pt = f"{self.coordinates[0]},{self.coordinates[1]},pm2dgl"
            elif mode == 2:
                self.pt = f"{address},pm2dgl"
        else:
            self.coordinates = ["0", "0"]
            self.info1 = "Ошибка адреса"
            self.info2 = ""
            self.pt = None

        self.info_label.setText(self.info1)

    def reset(self):
        self.pt = None
        self.info1 = ""
        self.info2 = ""
        self.info_label.setText(self.info1)
        self.get_response()
        self.image()

    def find(self):
        self.get_coordinates(self.find_line.text())
        self.get_response()
        self.image()


def main():
    window = YandexMap()
    window.show()
    app.exec()
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()