
import asyncio
import json
import uuid

from websockets.asyncio.server import serve

players = {}


async def handle_player(websocket):

    player_id = str(uuid.uuid4())

    players[player_id] = {
        "x": 60,
        "y": 450,
        "color": "Blue",
        "frame_index": 0,
        "facing_right": True,
        "is_idle": True,
    }

    print("Player joined:", player_id)

    # Tell the client its unique ID
    await websocket.send(json.dumps({
        "type": "welcome",
        "id": player_id
    }))

    try:
        async for message in websocket:

            data = json.loads(message)

            if player_id in players:
                players[player_id]["x"] = data["x"]
                players[player_id]["y"] = data["y"]
                players[player_id]["color"] = data["color"]
                players[player_id]["frame_index"] = data["frame_index"]
                players[player_id]["facing_right"] = data["facing_right"]
                players[player_id]["is_idle"] = data["is_idle"]

    except Exception as error:
        print("Player error:", error)

    finally:
        players.pop(player_id, None)
        print("Player left:", player_id)


async def broadcast():

    while True:

        await asyncio.sleep(1 / 20)

        message = json.dumps({
            "type": "state",
            "players": players
        })

        connections = list(server_connections)

        if connections:
            await asyncio.gather(
                *[
                    ws.send(message)
                    for ws in connections
                ],
                return_exceptions=True
            )


server_connections = set()


async def player_handler(websocket):

    server_connections.add(websocket)

    try:
        await handle_player(websocket)

    finally:
        server_connections.discard(websocket)


async def main():

    async with serve(
        player_handler,
        "0.0.0.0",
        8765
    ):

        print("Multiplayer server running!")

        await broadcast()


asyncio.run(main())
