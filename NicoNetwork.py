
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
        self.connection_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.send_queue = queue.Queue(maxsize=1)

    def connect(self):

        try:
            websocket = connect(self.address)

            with self.connection_lock:
                if self.stop_event.is_set():
                    websocket.close()
                    return False
                self.websocket = websocket

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
            while not self.stop_event.is_set():

                message = self.websocket.recv()
                data = json.loads(message)

                with self.lock:

                    if data["type"] == "welcome":
                        self.player_id = data["id"]
                        print("Your player ID:", self.player_id)

                    elif data["type"] == "state":
                        self.players = data["players"]

        except Exception as error:
            if not self.stop_event.is_set():
                print("Connection lost:", error)
        
    def send_data_thread(self):

        while not self.stop_event.is_set():

            try:

                data = self.send_queue.get(timeout=1)

                if self.websocket:
                    self.websocket.send(json.dumps(data))

            except queue.Empty:
                continue

            except Exception as error:

                if not self.stop_event.is_set():
                    print("Send error:", error)
                break

    def send_position(
        self, x, y, color, frame_index, facing_right, is_idle, grabbing=None
    ):

        data = {
            "x": x,
            "y": y,
            "color": color,
            "frame_index": frame_index,
            "facing_right": facing_right,
            "is_idle": is_idle,
            "grabbing": grabbing,
        }

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

        self.stop_event.set()

        with self.connection_lock:
            websocket = self.websocket

        if websocket:
            websocket.close()
