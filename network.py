
import json
import threading

from websockets.sync.client import connect


class NetworkClient:

    def __init__(self, address):
        self.address = address

        self.websocket = None

        self.players = {}
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.websocket = connect(
                self.address,
                legacy=True
            )

            print("Connected to multiplayer server!")

            thread = threading.Thread(
                target=self.receive_data,
                daemon=True
            )

            thread.start()

            return True

        except Exception as error:
            print("Connection failed:", error)
            return False

    def receive_data(self):

        while True:
            try:
                message = self.websocket.recv()

                data = json.loads(message)

                with self.lock:
                    self.players = data["players"]

            except Exception as error:
                print("Disconnected:", error)
                break

    def send_data(self, x, y, color):

        if self.websocket is None:
            return

        data = {
            "x": x,
            "y": y,
            "color": color
        }

        try:
            self.websocket.send(json.dumps(data))

        except Exception as error:
            print("Send failed:", error)

    def get_players(self):

        with self.lock:
            return self.players.copy()

    def close(self):

        if self.websocket:
            self.websocket.close()
