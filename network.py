
import json
import threading
import queue

from websockets.sync.client import connect


class NetworkClient:

    def __init__(self, address):

        self.address = address
        self.websocket = None

        self.player_id = None
        self.players = {}

        self.lock = threading.Lock()
        self.send_queue = queue.Queue(maxsize=1)

    def connect(self):

        try:
            self.websocket = connect(self.address)

            print("Connected to server!")

            threading.Thread(
                target=self.receive_data,
                daemon=True
            ).start()

            threading.Thread(
                target=self.send_data_thread,
                daemon=True
            ).start()

            return True

        except Exception as error:

            print("Connection failed:", error)
            return False

    def receive_data(self):

        try:
            while True:

                message = self.websocket.recv()
                data = json.loads(message)

                with self.lock:

                    if data["type"] == "welcome":
                        self.player_id = data["id"]
                        print("Your player ID:", self.player_id)

                    elif data["type"] == "state":
                        self.players = data["players"]

        except Exception as error:
            print("Connection lost:", error)
        
    def send_data_thread(self):

        while True:

            try:

                data = self.send_queue.get(timeout=1)

                if self.websocket:
                    self.websocket.send(json.dumps(data))

            except queue.Empty:
                continue

            except Exception as error:

                print("Send error:", error)
                break

    def send_position(self, x, y, color):

        data = {
            "x": x,
            "y": y,
            "color": color
        }

        # Keep only the newest movement update
        try:
            self.send_queue.put_nowait(data)

        except queue.Full:

            try:
                self.send_queue.get_nowait()
            except queue.Empty:
                pass

            self.send_queue.put_nowait(data)

    def get_players(self):

        with self.lock:

            return self.player_id, self.players.copy()

    def close(self):

        if self.websocket:
            self.websocket.close()
