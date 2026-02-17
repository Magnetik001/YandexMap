import os
import sys
import requests
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "MAP"
MAP_FILE = "../map.png"

API_KEY_GEOCODE = '8013b162-6b42-4997-9691-77b7074026e0'
API_KEY_STATIC = '2ac33b20-348f-4429-86d1-1ab126c72677'

address = input("Введите адрес: ")

response_geocode = requests.get(
    'http://geocode-maps.yandex.ru/1.x/',
    params={
        "apikey": API_KEY_GEOCODE,
        "geocode": address,
        "format": "json"
    }
)

if response_geocode.status_code != 200:
    print(f"Ошибка геосокодирования: {response_geocode.status_code}")
    print(response_geocode.text)
    sys.exit(1)

data = response_geocode.json()
try:
    coordinates = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
except (KeyError, IndexError):
    print("Не удалось найти координаты. Проверьте адрес.")
    print(data)
    sys.exit(1)

response_static_map = requests.get(
    'https://static-maps.yandex.ru/v1?',
    params={
        'apikey': API_KEY_STATIC,
        "ll": coordinates,
        "spn": "0.002,0.002"
    }
)

if response_static_map.status_code != 200:
    print(f"Ошибка загрузки карты: {response_static_map.status_code}")
    print("Ответ сервера:", response_static_map.text[:200])
    sys.exit(1)

content_type = response_static_map.headers.get('Content-Type', '')
if 'image' not in content_type.lower():
    print(f"Предупреждение: получен не image-контент! Content-Type: {content_type}")
    print("Первые байты ответа:", response_static_map.content[:100])


class GameView(arcade.Window):
    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()
        if hasattr(self, 'background'):
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(
                    (self.width - self.background.width) // 2,
                    (self.height - self.background.height) // 2,
                    self.background.width,
                    self.background.height
                ),
            )

    def get_image(self):
        with open(MAP_FILE, "wb") as file:
            file.write(response_static_map.content)

        if not os.path.exists(MAP_FILE) or os.path.getsize(MAP_FILE) == 0:
            print(f"Ошибка: файл {MAP_FILE} не создан или пустой!")
            return

        try:
            self.background = arcade.load_texture(MAP_FILE)
            print(f"Изображение загружено: {self.background.width}x{self.background.height}")
        except Exception as e:
            print(f"Не удалось загрузить изображение: {e}")
            print(f"Проверьте файл {os.path.abspath(MAP_FILE)} - возможно, это не PNG")
            sys.exit(1)


def main():
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)


if __name__ == "__main__":
    main()