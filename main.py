import os
import sys
from idlelib.rpc import response_queue

import requests
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"

server_address_geocode = 'https://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'

params_geocode = {
    "apikey": api_key_geocode,
    "geocode": input(),
    "format": "json"
}

response = requests.request("GET", server_address_geocode, params=params_geocode).json()

coordinates = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()


server_address_static_map = 'https://static-maps.yandex.ru/v1?'
api_key_static_map = '2ac33b20-348f-4429-86d1-1ab126c72677'

params_static_map = {
    "apikey": api_key_static_map,
    "ll": f"{coordinates[0]},{coordinates[1]}",
    "spn": "0.002,0.002"
}

response = requests.request("GET", server_address_static_map, params=params_static_map)


class GameView(arcade.Window):
    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()

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
            file.write(response.content)

        self.background = arcade.load_texture(MAP_FILE)


def main():
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()