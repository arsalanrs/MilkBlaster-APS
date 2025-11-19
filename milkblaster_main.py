import pygame
import sys
import random
import time
from PIL import Image

pygame.init()

# Basic setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Cow Chase Adventure")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
PINK = (170, 51, 106)
CYAN = (0, 255, 255)

FONT = pygame.font.SysFont("comicsans", 30)
BIG_FONT = pygame.font.SysFont("comicsans", 50)

clock = pygame.time.Clock()

player_size = 70
player_speed = 5
jump_strength = 15
gravity = 1
cow_speed = 3
level_attempts = 3
player_name = "Player"

# Initial loading
cow_img = pygame.image.load("Cow_cartoon_04.svg.png").convert_alpha()
cow_img_original = cow_img.copy()
bg_level1 = pygame.image.load("bglevel1.jpeg").convert()
lv1_blocks_img = pygame.image.load("lv1blocks.jpeg").convert_alpha()
opening_bg = pygame.image.load("openingpage.jpeg").convert()
controls_bg = pygame.image.load("WhatsApp Image 2025-11-19 at 00.04.47.jpeg").convert()
# cookie_img = pygame.image.load("images/cookie.png").convert_alpha()

def load_gif_frames(gif_path):
    frames = []
    gif = Image.open(gif_path)
    try:
        frame_num = 0
        while True:
            frame = gif.copy()
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            frame_str = frame.tobytes()
            frame_surf = pygame.image.frombytes(frame_str, frame.size, 'RGBA')
            frames.append(frame_surf.convert_alpha())
            frame_num += 1
            gif.seek(frame_num)
    except (EOFError, ValueError):
        pass
    return frames

# load gif
stickman_frames = load_gif_frames("output-onlinegiftools.gif")
stickman_frame_index = 0
stickman_frame_timer = 0
STICKMAN_ANIMATION_SPEED = 5

# --- LOAD AUDIO ---
# Sound effects (short sounds - .wav or .ogg recommended)
# jump_sound = pygame.mixer.Sound("sounds/jump.wav")
# cookie_sound = pygame.mixer.Sound("sounds/cookie.wav")
# shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
# hit_sound = pygame.mixer.Sound("sounds/hit.wav")

# Background music (longer audio - .mp3, .ogg, .wav)
# pygame.mixer.music.load("sounds/background_music.mp3")
# pygame.mixer.music.set_volume(0.5)  # Volume 0.0 to 1.0
# pygame.mixer.music.play(-1)  # -1 means loop forever, 0 means play once

# helpers
def draw_text_centered(text, font, color, surface, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y))
    surface.blit(render, rect)

def countdown():
    for i in range(3, 0, -1):
        WIN.fill(WHITE)
        draw_text_centered(f"Starting in {i}...", BIG_FONT, RED, WIN, HEIGHT//2)
        pygame.display.update()
        time.sleep(0.2)

def draw_stickman(x, y, color=BLUE):
    global stickman_frame_index, stickman_frame_timer, player_name

    if stickman_frames:
        stickman_frame_timer += 1
        if stickman_frame_timer >= STICKMAN_ANIMATION_SPEED:
            stickman_frame_timer = 0
            stickman_frame_index = (stickman_frame_index + 1) % len(stickman_frames)

        current_frame = stickman_frames[stickman_frame_index]
        scaled_frame = pygame.transform.scale(current_frame, (player_size, player_size))
        WIN.blit(scaled_frame, (x, y))
    else:
        # old stickman
        pygame.draw.circle(WIN, color, (x+20, y+20), 10)
        pygame.draw.line(WIN, color, (x+20, y+30), (x+20, y+50), 3)
        pygame.draw.line(WIN, color, (x+20, y+50), (x+10, y+70), 3)
        pygame.draw.line(WIN, color, (x+20, y+50), (x+30, y+70), 3)
        pygame.draw.line(WIN, color, (x+20, y+35), (x, y+45), 3)
        pygame.draw.line(WIN, color, (x+20, y+35), (x+40, y+45), 3)

    if player_name:
        name_font = pygame.font.SysFont("comicsans", 20)
        name_text = name_font.render(player_name, True, WHITE)
        name_x = x + (player_size // 2) - (name_text.get_width() // 2)
        name_y = y - 25
        WIN.blit(name_text, (name_x, name_y))

def draw_cow(x, y, facing_right=True, size=1):
    BASE_COW_WIDTH = 75
    BASE_COW_HEIGHT = 50
    scaled_width = int(BASE_COW_WIDTH * size)
    scaled_height = int(BASE_COW_HEIGHT * size)
    scaled_cow = pygame.transform.scale(cow_img_original, (scaled_width, scaled_height))

    if facing_right:
        scaled_cow = pygame.transform.flip(scaled_cow, True, False)

    WIN.blit(scaled_cow, (x, y))

def draw_cookie(x, y):
    pygame.draw.circle(WIN, ORANGE, (x+10, y+10), 10)
    # WIN.blit(cookie_img, (x, y))

# intro page
def get_player_name():
    global player_name
    name = ""
    entering = True
    opening_bg_scaled = pygame.transform.scale(opening_bg, (WIDTH, HEIGHT))
    
    while entering:
        WIN.blit(opening_bg_scaled, (0, 0))
        if name:
            draw_text_centered(name, FONT, WHITE, WIN, HEIGHT//2)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():
                        entering = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20 and event.unicode.isprintable():
                        name += event.unicode
    
    player_name = name.strip() if name.strip() else "Player"
    return player_name

def show_controls():
    controls_bg_scaled = pygame.transform.scale(controls_bg, (WIDTH, HEIGHT))
    
    showing = True
    while showing:
        WIN.blit(controls_bg_scaled, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                showing = False

# level system setup
def retry_level(level_func, attempts=level_attempts):
    if attempts == 0:
        main_menu()
        return
    success = level_func()

    if not success:
        if level_func == level3:
            return 'good ending'
        else:
            retry_level(level_func, attempts-1)

# levels
def level1():
    countdown()
    player = pygame.Rect(100, HEIGHT-100, player_size, player_size)
    cow = pygame.Rect(-200, HEIGHT-100, player_size, player_size)
    player_vel_y = 0
    on_ground = True

    platforms = [
        pygame.Rect(0, HEIGHT-50, WIDTH, 50),
        pygame.Rect(150, HEIGHT-150, 150, 20),
        pygame.Rect(400, HEIGHT-250, 150, 20),
        pygame.Rect(600, HEIGHT-180, 150, 20),
        pygame.Rect(300, HEIGHT-120, 100, 20),
        pygame.Rect(500, HEIGHT-350, 100, 20)
    ]

    cookies = [
        pygame.Rect(180, HEIGHT-180, 20, 20),
        pygame.Rect(220, HEIGHT-180, 20, 20),
        pygame.Rect(450, HEIGHT-280, 20, 20),
        pygame.Rect(500, HEIGHT-280, 20, 20),
        pygame.Rect(650, HEIGHT-210, 20, 20),
        pygame.Rect(700, HEIGHT-210, 20, 20),
        pygame.Rect(520, HEIGHT-370, 20, 20)
    ]

    bg_level1_scaled = pygame.transform.scale(bg_level1, (WIDTH, HEIGHT))
    
    run = True
    while run:
        clock.tick(30)
        WIN.blit(bg_level1_scaled, (0, 0))
        for plat in platforms:
            scaled_block = pygame.transform.scale(lv1_blocks_img, (plat.width, plat.height))
            WIN.blit(scaled_block, (plat.x, plat.y))
        for c in cookies:
            draw_cookie(c.x, c.y)
        draw_stickman(player.x, player.y, BLUE)
        draw_cow(cow.x, cow.y, facing_right=True)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = -jump_strength
            on_ground = False
            # jump_sound.play()

        player_vel_y += gravity
        player.y += player_vel_y
        on_ground = False
        for plat in platforms:
            if player.colliderect(plat) and player_vel_y >= 0:
                player.bottom = plat.top
                player_vel_y = 0
                on_ground = True

        if cow.x < player.x:
            cow.x += cow_speed*2
        elif cow.x > player.x:
            cow.x -= cow_speed*2
        if cow.y < player.y:
            cow.y += cow_speed
        elif cow.y > player.y:
            cow.y -= cow_speed
        if player.colliderect(cow):
            return False

        for c in cookies[:]:
            if player.colliderect(c):
                cookies.remove(c)
                # cookie_sound.play()

        if len(cookies) == 0:
            return True

def level2():
    countdown()
    rainbow_wires = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    wire_order = rainbow_wires.copy()
    random.shuffle(rainbow_wires)
    drawn_order = []

    run = True
    while run:
        WIN.fill(WHITE)
        draw_text_centered("Bomb Defusal!", BIG_FONT, BLACK, WIN, HEIGHT//7)
        draw_text_centered("Press 1-7 to cut wires", FONT, BLACK, WIN, HEIGHT//7+50)

        for i, color in enumerate(rainbow_wires):
            rect = pygame.Rect(155+i*80, HEIGHT//2, 20, 1000)
            pygame.draw.rect(WIN, pygame.Color(color), rect)
        draw_text_centered(' 1       2       3       4       5       6       7',
                           FONT, BLACK, WIN, HEIGHT//2 - 25)

        draw_text_centered(f"Cut sequence: {drawn_order}",
                           pygame.font.SysFont("comicsans", 20), BLACK, WIN, HEIGHT//4+50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                idx = None
                if event.key in [pygame.K_1, pygame.K_KP1]: idx = 0
                elif event.key in [pygame.K_2, pygame.K_KP2]: idx = 1
                elif event.key in [pygame.K_3, pygame.K_KP3]: idx = 2
                elif event.key in [pygame.K_4, pygame.K_KP4]: idx = 3
                elif event.key in [pygame.K_5, pygame.K_KP5]: idx = 4
                elif event.key in [pygame.K_6, pygame.K_KP6]: idx = 5
                elif event.key in [pygame.K_7, pygame.K_KP7]: idx = 6
                if idx is not None:
                    drawn_order.append(rainbow_wires[idx])
                    if drawn_order != wire_order[:len(drawn_order)]:
                        draw_text_centered("BOOM! Wrong wire!", BIG_FONT, RED, WIN, HEIGHT//2)
                        pygame.display.update()
                        time.sleep(2)
                        return False
                    if drawn_order == wire_order:
                        return True

def level3():
    countdown()
    run = True
    while run:
        WIN.fill(WHITE)
        draw_text_centered("Decision Time!", BIG_FONT, BLACK, WIN, HEIGHT//3)
        draw_text_centered("A: Give milk back", FONT, GREEN, WIN, HEIGHT//2)
        draw_text_centered("B: Run away", FONT, RED, WIN, HEIGHT//2 + 50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    WIN.fill(WHITE)
                    draw_text_centered("Cow is happy! You win!", BIG_FONT, GREEN, WIN, HEIGHT//2)
                    pygame.display.update()
                    time.sleep(3)
                    return False
                elif event.key == pygame.K_b:
                    return True

def level4():
    countdown()
    player = pygame.Rect(50, HEIGHT - 100, player_size, player_size)
    goal_x = WIDTH - 100

    greenmin, greenmax = 3, 5
    redmin, redmax = 2, 3

    run = True
    light = "GREEN"
    time_left = random.randint(greenmin, greenmax)
    last_tick = pygame.time.get_ticks()

    cow_x = WIDTH - 200
    cow_y = HEIGHT - 400

    while run:
        dt = (pygame.time.get_ticks() - last_tick) / 1000
        last_tick = pygame.time.get_ticks()
        time_left -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if light == "GREEN":
            if keys[pygame.K_RIGHT]:
                player.x += player_speed // 4
                if player.x >= goal_x:
                    return True
        else:
            if keys[pygame.K_RIGHT]:
                return False

        warning_text = ""
        if light == 'GREEN' and time_left <= 1:
            warning_text = '!!!'

        if time_left <= 0:
            if light == "GREEN":
                light = "RED"
                time_left = random.randint(redmin, redmax)
            else:
                light = "GREEN"
                time_left = random.randint(greenmin, greenmax)

        WIN.fill(WHITE)
        draw_stickman(player.x, player.y, BLUE)

        if light == "GREEN":
            draw_text_centered("GREEN LIGHT!", FONT, GREEN, WIN, 50)
        else:
            draw_text_centered("RED LIGHT!", FONT, RED, WIN, 50)

        if warning_text:
            draw_text_centered(warning_text, BIG_FONT, RED, WIN, 120)

        if light == "GREEN":
            draw_cow(cow_x, cow_y, facing_right=True, size=3)  # Flipped to look away
        else:
            draw_cow(cow_x, cow_y, facing_right=False, size=3)  # Not flipped, looks at player

        pygame.display.update()
        clock.tick(30)

def level5():
    countdown()

    player = pygame.Rect(100, HEIGHT - 100, player_size, player_size)
    player_y_vel = 0
    gravity = 1
    jump_power = -18
    cooldown_duration = 500
    last_key_press_time = 0
    on_ground = True

    cow = pygame.Rect(WIDTH - 150, HEIGHT, player_size, player_size)
    cow_direction = -1
    cow_speed = 3
    cow_lives = 3
    cow_shoot_timer = 0
    bullets_player = []
    bullets_cow = []

    run = True

    while run:
        dt = clock.tick(30)
        current_time = pygame.time.get_ticks()
        WIN.fill(WHITE)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and on_ground:
            player_y_vel = jump_power
            on_ground = False

        player_y_vel += gravity
        player.y += player_y_vel

        if player.y >= HEIGHT - 100:
            player.y = HEIGHT - 100
            player_y_vel = 0
            on_ground = True

        cow.y += cow_direction * cow_speed
        lowerlim = random.randint(200,300)
        upperlim = random.randint(50,100)
        if cow.y < lowerlim:
            cow.y = lowerlim
            cow_direction = 1
        elif cow.y > HEIGHT-upperlim:
            cow.y = HEIGHT-upperlim
            cow_direction = -1

        cow_shoot_timer -= 1*(1+(4-cow_lives)//5)
        if cow_shoot_timer <= 0:
            bullets_cow.append([cow.x, cow.y + 20])
            cow_shoot_timer = random.randint(40, 60)  # fire every 1.3–2 sec

        draw_stickman(player.x, player.y, BLUE)
        draw_cow(cow.x, cow.y)
        draw_text_centered("Press SPACE to shoot the cow | UP to jump", FONT, BLACK, WIN, 40)
        for b in bullets_player[:]:
            pygame.draw.circle(WIN, RED, (b[0], b[1]), 5)

            b[0] += 12
            if b[0] > WIDTH:
                bullets_player.remove(b)
                continue

            if cow.collidepoint(b[0], b[1]):
                bullets_player.remove(b)
                cow_lives -= 1
                if cow_lives <= 0:
                    WIN.fill(WHITE)
                    draw_text_centered("You win! Steak and milk!", BIG_FONT, GREEN, WIN, HEIGHT // 2)
                    pygame.display.update()
                    time.sleep(3)
                    return True

        for cb in bullets_cow[:]:
            pygame.draw.circle(WIN, PINK, (cb[0], cb[1]), 5)
            cb[0] -= 10
            if cb[0] < 0:
                bullets_cow.remove(cb)
            if player.collidepoint(cb[0], cb[1]):
                WIN.fill(WHITE)
                draw_text_centered("You were milk-blasted!", BIG_FONT, PINK, WIN, HEIGHT//2)
                pygame.display.update()
                time.sleep(3)
                return False
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_time - last_key_press_time >= cooldown_duration:
                        bullets_player.append([player.x + 20, player.y + 20])
                        last_key_press_time = current_time
                    # shoot_sound.play()


# menus
def main_menu():
    # pygame.mixer.music.play(-1)  # -1 loops forever
    
    player_name = get_player_name()
    show_controls()
    retry_level(level1)
    retry_level(level2)
    if retry_level(level3) != 'good ending':
        retry_level(level4)
        retry_level(level5)

    WIN.fill(WHITE)
    draw_text_centered("Congratulations! Game Complete!", BIG_FONT, GREEN, WIN, HEIGHT//2)
    pygame.display.update()
    time.sleep(5)
    pygame.quit()
    sys.exit()

main_menu()
