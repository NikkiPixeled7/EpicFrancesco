import pygame, socket, ipaddress
import tkinter as tk
import threading
from PIL import Image, ImageTk
from network import NetworkClient
from datetime import datetime, timezone

# ------------- Globals -------------

hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)
current_background = 0
background_photo = None
camera_x = 0
password_try = None

def daily_key():    
    today = datetime.now(timezone.utc).date()
    return today.toordinal()

def encode_ip(ip):
    ip_number = int(ipaddress.IPv4Address(ip))

    D = daily_key()
    key = (D * 5) ^ (D + 17) ^ (D * 3)

    if key % 7 == 0:
        encoded_number = ip_number ^ (key * 7)
    elif key % 5 == 0:
        encoded_number = ip_number ^ (key * 5)
    elif key % 3 == 0:
        encoded_number = ip_number ^ (key * 3)
    elif key % 2 == 0:
        encoded_number = ip_number ^ (key * 2)
    else:
        encoded_number = ip_number ^ key

    return format(encoded_number, "08X")

def decode_ip(code):

    encoded_number = int(code, 16)

    D = daily_key()
    key = (D * 5) ^ (D + 17) ^ (D * 3)

    if key % 7 == 0:
        ip_number = encoded_number ^ (key * 7)
    elif key % 5 == 0:
        ip_number = encoded_number ^ (key * 5)
    elif key % 3 == 0:
        ip_number = encoded_number ^ (key * 3)
    elif key % 2 == 0:
        ip_number = encoded_number ^ (key * 2)
    else:
        ip_number = encoded_number ^ key

    return str(ipaddress.IPv4Address(ip_number))

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

    def update(self, platforms):
        self.rect.x += self.vel_x

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                elif self.vel_x < 0:
                    self.rect.left = platform.right

        # 2. Vertical movement & collision
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True

                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        # 3. Ground detection probe (1 pixel directly below feet)
        ground_probe = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)
        self.on_ground = any(ground_probe.colliderect(platform) for platform in platforms)

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

network = None
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


    network_status = "Connected"

    running = True
    drag_offset_x = 0
    drag_offset_y = 0

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

        # ------------- UPDATE ------------

        if not editing:
            keys = pygame.key.get_pressed()

            player.handle_input(keys)
            player.update(platforms)
            player.update_animation(elapsed_ms)

            network.send_position(
                player.rect.x,
                player.rect.y,
                selected_character
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

        my_id, other_players = network.get_players()

        for player_id, data in other_players.items():

            if player_id == my_id:
                continue

            other_x = data["x"]
            other_y = data["y"]

            other_image = CHARACTER_IDLE_IMAGES.get(data["color"])
            if other_image is not None:
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

        if editing:
            instructions = [
                "EDIT MODE",
                "Left-click and drag a platform to move it",
                "P: add platform | Delete: remove selected platform",
                "TAB: play mode",
                "Code: " + encode_ip(host_ip),
            ]
            if selected_platform in platforms:
                platforms.remove(selected_platform)

        else:
            instructions = [
                "PLAY MODE",
                "A/D or Left/Right: move | Space/W/Up: jump",
                "1/2/3: change character | TAB: edit mode",
            ]

        instructions.append(f"Multiplayer: {network_status}")

        for i, line in enumerate(instructions):
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (15, 15 + i * 28))

        pygame.display.flip()

    network.close()
    pygame.quit()

#----------------- TKINTER MAIN GUI ------------------

def connect_to_server(ip):
    global network, network_status

    try:
        new_network = NetworkClient(f"ws://{ip}:8765")

        if new_network.connect():
            network = new_network
            network_status = "Connected"
            return True

        new_network.close()
        return False

    except Exception:
        return False

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

    
    # --------- GUI SETUP ---------

    play_image = Image.open("Assets/PlayButton.png")
    play_image_resized = play_image.resize(
        (100, 75),
        Image.Resampling.LANCZOS
    )
    play_photo_resized = ImageTk.PhotoImage(play_image_resized)

    # --------- CONNECTION HANDLING ---------
    
    def attempt_connection():

        nonlocal connecting

        if connecting:
            return

        entered_code = code_entry.get().strip()

        #HOST: No code entered
        if entered_code == "":
            target_ip = host_ip

        #JOIN: Code entered
        else:
            try:
                target_ip = decode_ip(entered_code)

            except (ValueError, ipaddress.AddressValueError):
                status_label.config(
                    text="INVALID CODE",
                    fg="red"
                )
                return

        connecting = True

        status_label.config(
            text="Connecting...",
            fg="blue"
        )

        def connection_thread():

            success = connect_to_server(target_ip)

            if success:
                window.after(
                    0,
                    lambda: [window.destroy(), main_loop()]
                )

            else:
                def connection_failed():
                    nonlocal connecting
                    connecting = False

                    status_label.config(
                        text="INVALID CODE - Try again or leave blank to host",
                        fg="red"
                    )

                window.after(0, connection_failed)

        threading.Thread(
            target=connection_thread,
            daemon=True
        ).start()

        # --------- PLAY BUTTON ---------

    start_button = tk.Button(
        window,
        image=play_photo_resized,
        command=attempt_connection,
        borderwidth=0,
        highlightthickness=0,
        relief="flat"
    )

    start_button.pack(pady=5)

    code_entry = tk.Entry(
        window,
        width=20,
        font=("Arial", 14)
    )
    code_entry.pack(pady=10)

    status_label = tk.Label(
        window,
        text="Enter code to join or leave blank to host",
        font=("Arial", 11),
        fg="white",
        bg="black"
    )
    status_label.pack(pady=5)

    connecting = False

    window.mainloop()


main_menu_loop()
pygame.quit()
