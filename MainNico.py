import pygame
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
ANIMATION_FRAME_DURATION = 100

# -------------------- CHARACTER OPTIONS --------------------

CHARACTERS = {
    "Francesco": WHITE,
    "Green": GREEN,
    "Brown": BROWN,
}

selected_character = "Francesco"
CHARACTER_IDLE_IMAGES = {}



class Player:
    def __init__(self, x, y, chosenCharacter=None):
        self.rect = pygame.Rect(x, y, 30, 40)
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

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
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
            color,
            (
                x,
                self.rect.y,
                self.rect.width,
                self.rect.height,
            ),
        )

# -------------------- ANIMATIONS TESTING 11/3/26 --------------------
SCALE = 5
francesco = [
pygame.transform.scale(pygame.image.load(f"francesco_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

francesco.append(pygame.transform.scale(pygame.image.load("francesco_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Francesco"] = francesco
CHARACTER_IDLE_IMAGES["Francesco"] = pygame.transform.scale(
    pygame.image.load("francesco_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)

SCALE = 5
giuseppe = [
pygame.transform.scale(pygame.image.load(f"giuseppe_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

giuseppe.append(pygame.transform.scale(pygame.image.load("giuseppe_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Giuseppe"] = giuseppe
CHARACTER_IDLE_IMAGES["Giuseppe"] = pygame.transform.scale(
    pygame.image.load("giuseppe_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)

SCALE = 5
alfredo = [
pygame.transform.scale(pygame.image.load(f"alfredo_{i}.png").convert_alpha(), (11 * SCALE, 15 * SCALE)) for i
        in range(3)]

# the file names will be "SkinName" followed by a number increasing by 1 in order of animation, range is lowest number to highest number plus one

alfredo.append(pygame.transform.scale(pygame.image.load("alfredo_jump.png").convert_alpha(), (11 * SCALE, 15 * SCALE)))
CHARACTERS["Alfredo"] = alfredo
CHARACTER_IDLE_IMAGES["Alfredo"] = pygame.transform.scale(
    pygame.image.load("alfredo_idle.png").convert_alpha(),
    (11 * SCALE, 15 * SCALE),
)


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

# -------------------- GAME SETUP --------------------

player = Player(60, 450, CHARACTERS[selected_character])
player.idle_image = CHARACTER_IDLE_IMAGES.get(selected_character)
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

    # -------------------- EVENTS --------------------

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
                selected_character = "Francesco"
                player.chosenCharacter = CHARACTERS[selected_character]
                player.idle_image = CHARACTER_IDLE_IMAGES.get(selected_character)

            elif event.key == pygame.K_2:
                selected_character = "Giuseppe"
                player.chosenCharacter = CHARACTERS[selected_character]
                player.idle_image = CHARACTER_IDLE_IMAGES.get(selected_character)

            elif event.key == pygame.K_3:
                selected_character = "Alfredo"
                player.chosenCharacter = CHARACTERS[selected_character]
                player.idle_image = CHARACTER_IDLE_IMAGES.get(selected_character)

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

    # -------------------- UPDATE --------------------

    if not editing:
        keys = pygame.key.get_pressed()

        player.handle_input(keys)
        player.update(platforms)
        player.update_animation(clock.get_time())

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

    # -------------------- DRAW --------------------

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
