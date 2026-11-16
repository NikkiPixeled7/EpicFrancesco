import pygame
import tkinter as tk
import threading
from tkinter import ttk
from PIL import Image, ImageTk
from network import NetworkClient
import socket

# ------------- Globals -------------

hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)
current_background = 0
background_photo = None
camera_x = 0

pygame.init()

def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 35
    window.geometry(f"{width}x{height}+{x}+{y}")

# -------------------- SETTINGS --------------------

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
REMOTE_SMOOTHING_MS = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Character and Customizable Map")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (80, 150, 230)
GREEN = (90, 180, 100)
BROWN = (130, 95, 65)

MOVE_SPEED = 5
GRAVITY = 0.7
JUMP_STRENGTH = -13
ANIMATION_FRAME_DURATION = 100
GRAPPLE_RANGE = 60

# -------------- CHARACTER OPTIONS -----------------
# -------------------- CHARACTER OPTIONS --------------------

CHARACTERS = {
    "Blue": BLUE,
    "Francesco": WHITE,
    "Green": GREEN,
    "Brown": BROWN,
}

selected_character = "Blue"
selected_character = "Francesco"
CHARACTER_IDLE_IMAGES = {}



class Player:
    def __init__(self, x, y, chosenCharacter=None):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.vel_x = self.vel_y = 0
        self.chosenCharacter = chosenCharacter or []
        self.on_ground = False
        self.frame_index = 0
        self.frame_timer = 0
        self.facing_right = True
        self.air_timer = 0
        self.spawn_x = 15
        self.spawn_y = 250
        self.idle_image = None

    def handle_input(self, keys):
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_UP]
            or keys[pygame.K_w]
        ) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def update(self, platforms, player_colliders=()):
        for other_rect, push_right in player_colliders:
            if self.rect.colliderect(other_rect):
                if self.rect.centerx < other_rect.centerx:
                    self.rect.right = other_rect.left
                elif self.rect.centerx > other_rect.centerx:
                    self.rect.left = other_rect.right
                elif push_right:
                    self.rect.left = other_rect.right
                else:
                    self.rect.right = other_rect.left

        self.rect.x += self.vel_x

        obstacles = tuple(platforms) + tuple(
            other_rect for other_rect, _ in player_colliders
        )

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.vel_x > 0:
                    self.rect.right = obstacle.left
                elif self.vel_x < 0:
                    self.rect.left = obstacle.right

        # 2. Vertical movement & collision
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.vel_y > 0:
                    self.rect.bottom = obstacle.top
                    self.vel_y = 0
                    self.on_ground = True

                elif self.vel_y < 0:
                    self.rect.top = obstacle.bottom
                    self.vel_y = 0

        # 3. Ground detection probe (1 pixel directly below feet)
        ground_probe = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)
        self.on_ground = any(
            ground_probe.colliderect(obstacle) for obstacle in obstacles
        )

        # 4. Prevent gravity accumulation while standing on ground
        if self.on_ground and self.vel_y > 0:
            self.vel_y = 0

    def update_animation(self, elapsed_ms):
        if not isinstance(self.chosenCharacter, list) or not self.chosenCharacter:
            return

        jump_frame_index = len(self.chosenCharacter) - 1
        if not self.on_ground:
            self.frame_index = jump_frame_index
            self.frame_timer = 0
        elif self.vel_x == 0:
            self.frame_index = 0
            self.frame_timer = 0
        else:
            walk_frame_count = jump_frame_index
            self.frame_timer += elapsed_ms
            frames_elapsed = self.frame_timer // ANIMATION_FRAME_DURATION
            self.frame_index = (self.frame_index + frames_elapsed) % walk_frame_count
            self.frame_timer %= ANIMATION_FRAME_DURATION

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x

        if self.idle_image is not None and self.on_ground and self.vel_x == 0:
            image = self.idle_image
            if not self.facing_right:
                image = pygame.transform.flip(image, True, False)
            frame_rect = image.get_rect(
                midbottom=(x + self.rect.width // 2, self.rect.bottom)
            )
            surface.blit(image, frame_rect)
            return

        if isinstance(self.chosenCharacter, list) and self.chosenCharacter:
            frame = self.chosenCharacter[self.frame_index % len(self.chosenCharacter)]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)

            frame_rect = frame.get_rect(midbottom=(x + self.rect.width // 2, self.rect.bottom))
            surface.blit(frame, frame_rect)
            return

        color = self.chosenCharacter or WHITE
        pygame.draw.rect(
            surface,
            self.color,
            color,
            (
                self.rect.x - camera_x,
                x,
                self.rect.y,
                self.rect.width,
                self.rect.height,
            ),
        )

# -------------------- ANIMATIONS TESTING 11/3/26 --------------------
SCALE = 5
francesco = [
pygame.transform.scale(pygame.image.load(f"Assets/francesco_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

francesco.append(pygame.transform.scale(pygame.image.load("Assets/francesco_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Francesco"] = francesco
CHARACTER_IDLE_IMAGES["Francesco"] = pygame.transform.scale(
    pygame.image.load("Assets/francesco_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)

SCALE = 5
giuseppe = [
pygame.transform.scale(pygame.image.load(f"Assets/giuseppe_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

giuseppe.append(pygame.transform.scale(pygame.image.load("Assets/giuseppe_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Giuseppe"] = giuseppe
CHARACTER_IDLE_IMAGES["Giuseppe"] = pygame.transform.scale(
    pygame.image.load("Assets/giuseppe_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)

SCALE = 5
alfredo = [
pygame.transform.scale(pygame.image.load(f"Assets/alfredo_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

alfredo.append(pygame.transform.scale(pygame.image.load("Assets/alfredo_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Alfredo"] = alfredo
CHARACTER_IDLE_IMAGES["Alfredo"] = pygame.transform.scale(
    pygame.image.load("Assets/alfredo_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)

class enemy1:
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vel_x = 2
        self.vel_y = 0
        self.on_ground = False
        self.images = [
            pygame.transform.scale(
                pygame.image.load(f"Assets/enemy1_{i}.png").convert_alpha(),
                (11 * SCALE, 15 * SCALE),
            )
            for i in range(3)
        ]
        self.frame_index = 0
        self.frame_timer = 0

    def update(self, platforms, elapsed_ms):
        self.frame_timer += elapsed_ms
        frames_elapsed = self.frame_timer // ANIMATION_FRAME_DURATION
        if frames_elapsed:
            self.frame_index = (self.frame_index + frames_elapsed) % len(self.images)
            self.frame_timer %= ANIMATION_FRAME_DURATION

# ----------------- MAP ----------------
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                    self.vel_x *= -1
                elif self.vel_x < 0:
                    self.rect.left = platform.right
                    self.vel_x *= -1

        # Vertical movement & collision
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        # Ground detection probe (1 pixel directly below feet)
        ground_probe = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)
        self.on_ground = any(ground_probe.colliderect(platform) for platform in platforms)

        # Prevent gravity accumulation while standing on ground
        if self.on_ground and self.vel_y > 0:
            self.vel_y = 0

    def draw(self, surface, camera_x):
        image = self.images[self.frame_index]
        if self.vel_x < 0:
            image = pygame.transform.flip(image, True, False)
        image_rect = image.get_rect(
            midbottom=(self.rect.centerx - camera_x, self.rect.bottom)
        )
        surface.blit(image, image_rect)
            
def weight():
    pass    





# below is oop, from a player class

# -------------------- MAP --------------------

platforms = [
    pygame.Rect(0, 540, 500, 60),
    pygame.Rect(250, 430, 150, 20),
    pygame.Rect(520, 480, 180, 20),
    pygame.Rect(780, 390, 150, 20),
    pygame.Rect(1100, 540, 500, 60),
]

MAP_WIDTH = 1600

# ---------------- GAME SETUP -------------
# -------------------- GAME SETUP --------------------

player = Player(60, 450, CHARACTERS[selected_character])
player.idle_image = CHARACTER_IDLE_IMAGES.get(selected_character)
enemy = enemy1(300, 390)
camera_x = 0

editing = True
selected_platform = None

platform_width = 150
platform_height = 20

# ---------------- MULTIPLAYER ----------------

network = NetworkClient(f"ws://{host_ip}:8765")
network_status = "Not connected"


def connect_to_server():
    global network_status

    if network.connect():
        network_status = "Connected"
    else:
        network_status = "Offline (server unavailable)"

def main_loop(): # function for start so no need to change running variable

    global editing, selected_platform, selected_character, camera_x, network_status

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Character and Customizable Map")

    network_status = "Connecting..."
    threading.Thread(target=connect_to_server, daemon=True).start()

    running = True
    drag_offset_x = 0
    drag_offset_y = 0
    remote_positions = {}
    grapple_target = None
    is_held = False

    while running:
        elapsed_ms = clock.tick(FPS)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x

        # -------------- EVENTS --------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_TAB:
                    editing = not editing
                    selected_platform = None
                    player.vel_x = 0
                    player.vel_y = 0
                    if editing:
                        grapple_target = None
                        network.send_position(
                            player.rect.x,
                            player.rect.y,
                            selected_character,
                            player.frame_index,
                            player.facing_right,
                            player.on_ground and player.vel_x == 0,
                            None,
                        )

                if not editing and event.key == pygame.K_e:
                    if grapple_target is not None:
                        grapple_target = None
                    else:
                        current_id, current_players = network.get_players()
                        already_held = any(
                            data.get("grabbing") == current_id
                            for player_id, data in current_players.items()
                            if player_id != current_id
                        )
                        candidates = []

                        if current_id is not None and not already_held:
                            for other_id, (other_x, other_y) in remote_positions.items():
                                if other_id not in current_players:
                                    continue
                                already_grabbed = any(
                                    data.get("grabbing") == other_id
                                    for player_id, data in current_players.items()
                                    if player_id != current_id
                                )
                                if already_grabbed:
                                    continue

                                dx = player.rect.centerx - (other_x + 15)
                                dy = player.rect.centery - (other_y + 20)
                                distance_squared = dx * dx + dy * dy
                                if distance_squared <= GRAPPLE_RANGE * GRAPPLE_RANGE:
                                    candidates.append((distance_squared, other_id))

                        if candidates:
                            grapple_target = min(candidates)[1]

                if editing and event.key == pygame.K_p:
                    platforms.append(
                        pygame.Rect(
                            world_mouse_x,
                            mouse_y,
                            platform_width,
                            platform_height,
                        )
                    )

                if (
                    editing
                    and event.key == pygame.K_DELETE
                    and selected_platform is not None
                ):
                    if selected_platform in platforms:
                        platforms.remove(selected_platform)

                    selected_platform = None

                if not editing:
                    character_keys = {
                        pygame.K_1: "Francesco",
                        pygame.K_2: "Giuseppe",
                        pygame.K_3: "Alfredo",
                    }
                    if event.key in character_keys:
                        selected_character = character_keys[event.key]
                        player.chosenCharacter = CHARACTERS[selected_character]
                        player.idle_image = CHARACTER_IDLE_IMAGES.get(
                            selected_character
                        )

            if editing and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_platform = None

                    for platform in reversed(platforms):
                        if platform.collidepoint(world_mouse_x, mouse_y):
                            selected_platform = platform

                            drag_offset_x = world_mouse_x - platform.x
                            drag_offset_y = mouse_y - platform.y
                            break

            if editing and event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_platform = None

        if not running:
            break

        my_id, other_players = network.get_players()

        # ------------- UPDATE ------------

        if not editing:
            is_held = my_id is not None and any(
                data.get("grabbing") == my_id
                for player_id, data in other_players.items()
                if player_id != my_id
            )

            if grapple_target is not None:
                target_position = remote_positions.get(grapple_target)
                if grapple_target not in other_players or target_position is None:
                    grapple_target = None
                else:
                    dx = player.rect.centerx - (target_position[0] + 15)
                    dy = player.rect.centery - (target_position[1] + 20)
                    if dx * dx + dy * dy > GRAPPLE_RANGE * GRAPPLE_RANGE:
                        grapple_target = None

            keys = pygame.key.get_pressed()

            if is_held:
                player.vel_x = 0
                player.vel_y = 0
            else:
                player.handle_input(keys)
                player_colliders = [
                    (
                        pygame.Rect(round(x), round(y), 30, 40),
                        my_id > player_id,
                    )
                    for player_id, (x, y) in remote_positions.items()
                    if my_id is not None
                ]
                player.update(platforms, player_colliders)
            player.update_animation(elapsed_ms)

            network.send_position(
                player.rect.x,
                player.rect.y,
                selected_character,
                player.frame_index,
                player.facing_right,
                player.on_ground and player.vel_x == 0,
                grapple_target,
            )

            if player.rect.top > SCREEN_HEIGHT + 200:
                player.rect.topleft = (60, 450)
                player.vel_x = 0
                player.vel_y = 0

            camera_x = player.rect.centerx - SCREEN_WIDTH // 2

            camera_x = max(
                0,
                min(camera_x, MAP_WIDTH - SCREEN_WIDTH),
            )

        else:
            if pygame.mouse.get_pressed()[0] and selected_platform is not None:
                selected_platform.x = world_mouse_x - drag_offset_x
                selected_platform.y = mouse_y - drag_offset_y

        # -------------- DRAW ---------------

        screen.fill((135, 206, 235))

        for platform in platforms:
            screen_rect = pygame.Rect(
                platform.x - camera_x,
                platform.y,
                platform.width,
                platform.height,
            )

            pygame.draw.rect(screen, BROWN, screen_rect)

        player.draw(screen, camera_x)

        # ------------- OTHER PLAYERS -------------

        active_remote_ids = set()

        for player_id, data in other_players.items():

            if player_id == my_id:
                continue

            active_remote_ids.add(player_id)
            target_x = data["x"]
            target_y = data["y"]
            if player_id not in remote_positions:
                remote_positions[player_id] = (target_x, target_y)
            else:
                current_x, current_y = remote_positions[player_id]
                smoothing = min(1.0, elapsed_ms / REMOTE_SMOOTHING_MS)
                remote_positions[player_id] = (
                    current_x + (target_x - current_x) * smoothing,
                    current_y + (target_y - current_y) * smoothing,
                )
            smoothed_x, smoothed_y = remote_positions[player_id]
            other_x = round(smoothed_x)
            other_y = round(smoothed_y)
            character_frames = CHARACTERS.get(data["color"])
            is_idle = data.get("is_idle", True)

            if is_idle:
                other_image = CHARACTER_IDLE_IMAGES.get(data["color"])
            elif isinstance(character_frames, list) and character_frames:
                frame_index = data.get("frame_index", 0) % len(character_frames)
                other_image = character_frames[frame_index]
            else:
                other_image = None

            if other_image is not None:
                if not data.get("facing_right", True):
                    other_image = pygame.transform.flip(other_image, True, False)
                image_rect = other_image.get_rect(
                    midbottom=(other_x - camera_x + 15, other_y + 40)
                )
                screen.blit(other_image, image_rect)
            else:
                other_color = CHARACTERS.get(data["color"], BLUE)
                if isinstance(other_color, list):
                    other_color = BLUE

                pygame.draw.rect(
                    screen,
                    other_color,
                    (
                        other_x - camera_x,
                        other_y,
                        30,
                        40
                    )
                )

        for holder_id, data in other_players.items():
            target_id = data.get("grabbing")
            if target_id is None:
                continue

            holder_position = (
                (player.rect.x, player.rect.y)
                if holder_id == my_id
                else remote_positions.get(holder_id)
            )
            target_position = (
                (player.rect.x, player.rect.y)
                if target_id == my_id
                else remote_positions.get(target_id)
            )
            if holder_position is None or target_position is None:
                continue

            pygame.draw.line(
                screen,
                (190, 45, 45),
                (
                    round(holder_position[0]) - camera_x + 15,
                    round(holder_position[1]) + 20,
                ),
                (
                    round(target_position[0]) - camera_x + 15,
                    round(target_position[1]) + 20,
                ),
                3,
            )

        for player_id in list(remote_positions):
            if player_id not in active_remote_ids:
                del remote_positions[player_id]

        if editing:
            instructions = [
                "EDIT MODE",
                "Left-click and drag a platform to move it",
                "P: add platform | Delete: remove selected platform",
                "TAB: play mode",
            ]
            if selected_platform in platforms:
                platforms.remove(selected_platform)

        else:
            instructions = [
                "PLAY MODE",
                "A/D or Left/Right: move | Space/W/Up: jump",
                "1/2/3: change character | TAB: edit mode",
                "E: grapple/release a nearby player",
            ]
            if is_held:
                instructions.append("Grappled: you cannot move")

        instructions.append(f"Multiplayer: {network_status}")

        for i, line in enumerate(instructions):
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (15, 15 + i * 28))

        pygame.display.flip()

    network.close()
    pygame.quit()

#----------------- TKINTER MAIN GUI ------------------

def main_menu_loop():

    # ---------- Window Setup ----------

    # background image list

    background_images = [
        "Assets/MainMenuN.png",
        "Assets/MainMenuP1.png",
        "Assets/MainMenuP2.png",
        "Assets/MainMenuP3.png",
        "Assets/MainMenuP4.png",
        "Assets/MainMenuP3.png",
        "Assets/MainMenuP2.png",
        "Assets/MainMenuP1.png",
        "Assets/MainMenuN.png",
        "Assets/MainMenuN1.png",
        "Assets/MainMenuN2.png",
        "Assets/MainMenuN3.png",
        "Assets/MainMenuN4.png",
        "Assets/MainMenuN3.png",
        "Assets/MainMenuN2.png",
        "Assets/MainMenuN1.png"
    ]

    # intervals

    normal_intervals = 50
    long_intervals = 150

    # image animation function

    def animate_background():

        global current_background, background_photo

        background_image = Image.open(background_images[current_background])
        background_image_resized = background_image.resize((1000, 600), Image.Resampling.LANCZOS)
        background_photo = ImageTk.PhotoImage(background_image_resized)
        background_label.config(image=background_photo)

        if current_background == 4 or current_background == 12:
            delay = long_intervals
        else:
            delay = normal_intervals

        current_background += 1

        if current_background >= len(background_images):
            current_background = 0

        window.after(delay, animate_background)

    window = tk.Tk()
    window.title("Epic Francesco - Main Menu")
    center_window(window, 1000, 600)

    spacing_frame = tk.Frame(window, height=170)
    spacing_frame.pack(side="top")

    background_label = tk.Label(window)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    animate_background()

    # --------- Gui Setup ---------

    play_image = Image.open("Assets/PlayButton.png")
    play_image_resized = play_image.resize((100, 75), Image.Resampling.LANCZOS)
    play_photo_resized = ImageTk.PhotoImage(play_image_resized)

    start_button = tk.Button(window, image=play_photo_resized, command=lambda: [window.destroy(), main_loop()], borderwidth=0, highlightthickness=0, relief="flat")
    start_button.pack(pady=5)

    window.mainloop()   

main_menu_loop()
pygame.quit()
