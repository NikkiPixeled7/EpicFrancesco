import asyncio
import json
import uuid

from websockets.asyncio.server import serve

players = {}


async def send_game_state():
    while True:
        await asyncio.sleep(1 / 30)

        game_state = {
            "players": {
                player_id: {
                    "x": player["x"],
                    "y": player["y"],
                    "color": player["color"]
                }

                for player_id, player in players.items()
            }
        }

        message = json.dumps(game_state)

        for player in list(players.values()):
            websocket = player["websocket"]

            try:
                await websocket.send(message)

            except Exception:
                pass

async def handle_player(websocket):
    player_id = str(uuid.uuid4())

    players[player_id] = {
        "x": 60,
        "y": 450,
        "color": "blue",
        "websocket": websocket
    }

    print("Player connected:", player_id)

    try:
        async for message in websocket:
            data = json.loads(message)

            if player_id in players:
                players[player_id]["x"] = data["x"]
                players[player_id]["y"] = data["y"]
                players[player_id]["color"] = data["color"]
    except Exception as error:
        print("Connection error:", error)

    finally:
        players.pop(player_id, None)

        print("Player disconnected:", player_id)

async def main():
    async with serve(handle_player, "0.0.0.0", 8765):
        print("Multiplayer server running on port 8765")

        await send_game_state()

asyncio.run(main())
