import pygame
from network import NetworkClient

pygame.init()

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

# -------------- CHARACTER OPTIONS -----------------

CHARACTERS = {
    "Blue": BLUE,
    "Green": GREEN,
    "Brown": BROWN,
}

selected_character = "Blue"


class Player:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def handle_input(self, keys):
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED

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

    def draw(self, surface, camera_x):
        pygame.draw.rect(
            surface,
            self.color,
            (
                self.rect.x - camera_x,
                self.rect.y,
                self.rect.width,
                self.rect.height,
            ),
        )


# ----------------- MAP ----------------

platforms = [
    pygame.Rect(0, 540, 500, 60),
    pygame.Rect(250, 430, 150, 20),
    pygame.Rect(520, 480, 180, 20),
    pygame.Rect(780, 390, 150, 20),
    pygame.Rect(1100, 540, 500, 60),
]

MAP_WIDTH = 1600

# ---------------- GAME SETUP -------------

player = Player(60, 450, CHARACTERS[selected_character])
camera_x = 0

editing = True
selected_platform = None

platform_width = 150
platform_height = 20

running = True

while running:
    clock.tick(FPS)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    world_mouse_x = mouse_x + camera_x

    # ------------- MULTIPLAYER ----------------

    network = NetworkClient("ws://127.0.0.1:8765")

    connected = network.connect()

    if not connected:
        pygame.quit()
        exit()

    # -------------- EVENTS --------------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_TAB:
                editing = not editing
                selected_platform = None
                player.vel_x = 0
                player.vel_y = 0

            if event.key == pygame.K_1:
                selected_character = "Blue"
                player.color = CHARACTERS[selected_character]

            elif event.key == pygame.K_2:
                selected_character = "Green"
                player.color = CHARACTERS[selected_character]

            elif event.key == pygame.K_3:
                selected_character = "Brown"
                player.color = CHARACTERS[selected_character]

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

    # ------------- UPDATE ------------

    
    if not editing:
        keys = pygame.key.get_pressed()

        player.handle_input(keys)
        player.update(platforms)

        network.send_data(
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
        if (
            pygame.mouse.get_pressed()[0]
            and selected_platform is not None
        ):
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

    # ------------ OTHER PLAYERS -----------

    other_players = network.get_players()

    for player_id, data in other_players.items():

        other_x = data["x"]
        other_y = data["y"]

        other_color = CHARACTERS.get(
            data["color"],
            BLUE
        )

        # other player draw section
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
        ]

    else:
        instructions = [
            "PLAY MODE",
            "A/D or Left/Right: move | Space/W/Up: jump",
            "1/2/3: change character | TAB: edit mode",
        ]

    for i, line in enumerate(instructions):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (15, 15 + i * 28))

    pygame.display.flip()

pygame.quit()
