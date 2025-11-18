import pygame
import sys
import random
import time
from PIL import Image

pygame.init()

# --- SCREEN SETUP ---
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Cow Chase Adventure")

# --- COLORS --- Setting PYGAME WINDOW COLORS
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

# --- FONTS ---
FONT = pygame.font.SysFont("comicsans", 30)
BIG_FONT = pygame.font.SysFont("comicsans", 50)

# --- CLOCK ---
clock = pygame.time.Clock()

# --- LOAD IMAGES (PNG) ---
# Load cow image
cow_img = pygame.image.load("Cow_cartoon_04.svg.png").convert_alpha()
cow_img_original = cow_img.copy()  # Keep original for scaling

# Load level 1 background and blocks
bg_level1 = pygame.image.load("bglevel1.jpeg").convert()
lv1_blocks_img = pygame.image.load("lv1blocks.jpeg").convert_alpha()

# Load opening page background
opening_bg = pygame.image.load("openingpage.jpeg").convert()

# Load controls menu background
controls_bg = pygame.image.load("WhatsApp Image 2025-11-19 at 00.04.47.jpeg").convert()

# --- LOAD STICKMAN GIF ANIMATION ---
def load_gif_frames(gif_path):
    """Load GIF and extract all frames as pygame surfaces"""
    frames = []
    gif = Image.open(gif_path)
    try:
        frame_num = 0
        while True:
            # Convert PIL image to pygame surface
            frame = gif.copy()
            # Convert to RGBA if needed
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            # Convert to pygame surface (using frombytes for compatibility)
            frame_str = frame.tobytes()
            try:
                frame_surf = pygame.image.frombytes(frame_str, frame.size, 'RGBA')
            except AttributeError:
                # Fallback for older pygame versions
                frame_surf = pygame.image.fromstring(frame_str, frame.size, 'RGBA')
            frames.append(frame_surf.convert_alpha())
            
            frame_num += 1
            gif.seek(frame_num)
    except (EOFError, ValueError):
        pass  # End of GIF
    return frames

# Load stickman GIF frames
stickman_frames = load_gif_frames("output-onlinegiftools.gif")
stickman_frame_index = 0
stickman_frame_timer = 0
STICKMAN_ANIMATION_SPEED = 5  # Frames per animation frame (lower = faster)

# Example: Load cookie images (if you have them)
# cookie_img = pygame.image.load("images/cookie.png").convert_alpha()

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

# --- GAME VARIABLES ---
player_size = 70  # Increased size for stickman GIF
player_speed = 5
jump_strength = 15
gravity = 1
cow_speed = 3
level_attempts = 3
player_name = "Player"  # Global player name

# --- HELPER FUNCTIONS ---
def draw_text_centered(text, font, color, surface, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y))
    surface.blit(render, rect)

def countdown():
    for i in range(3, 0, -1):
        WIN.fill(WHITE)
        draw_text_centered(f"Starting in {i}...", BIG_FONT, RED, WIN, HEIGHT//2)
        pygame.display.update()
        time.sleep(0.1)

def draw_stickman(x, y, color=BLUE):
    global stickman_frame_index, stickman_frame_timer, player_name
    
    # Use animated GIF frames
    if stickman_frames:
        # Update animation frame
        stickman_frame_timer += 1
        if stickman_frame_timer >= STICKMAN_ANIMATION_SPEED:
            stickman_frame_timer = 0
            stickman_frame_index = (stickman_frame_index + 1) % len(stickman_frames)
        
        # Get current frame and scale to match player_size
        current_frame = stickman_frames[stickman_frame_index]
        scaled_frame = pygame.transform.scale(current_frame, (player_size, player_size))
        WIN.blit(scaled_frame, (x, y))
    else:
        # Fallback: Draw with shapes if GIF failed to load
        pygame.draw.circle(WIN, color, (x+20, y+20), 10)
        pygame.draw.line(WIN, color, (x+20, y+30), (x+20, y+50), 3)
        pygame.draw.line(WIN, color, (x+20, y+50), (x+10, y+70), 3)
        pygame.draw.line(WIN, color, (x+20, y+50), (x+30, y+70), 3)
        pygame.draw.line(WIN, color, (x+20, y+35), (x, y+45), 3)
        pygame.draw.line(WIN, color, (x+20, y+35), (x+40, y+45), 3)
    
    # Draw player name above the stickman
    if player_name:
        name_font = pygame.font.SysFont("comicsans", 20)
        name_text = name_font.render(player_name, True, WHITE)
        # Center the name above the character
        name_x = x + (player_size // 2) - (name_text.get_width() // 2)
        name_y = y - 25
        WIN.blit(name_text, (name_x, name_y))

def draw_cow(x, y, facing_right=True, size=1):
    # Base size matching the original cow shape dimensions (increased)
    # Original shape: body 40x30 + head extension = ~60x40 pixels at size=1
    # Increased to 75x50 for better visibility
    BASE_COW_WIDTH = 75
    BASE_COW_HEIGHT = 50
    
    # Calculate scaled size to match original shape size
    scaled_width = int(BASE_COW_WIDTH * size)
    scaled_height = int(BASE_COW_HEIGHT * size)
    
    # Scale the image to match original cow shape size
    scaled_cow = pygame.transform.scale(cow_img_original, (scaled_width, scaled_height))
    
    # Flip horizontally if facing left
    if not facing_right:
        scaled_cow = pygame.transform.flip(scaled_cow, True, False)
    
    # Draw the cow image
    WIN.blit(scaled_cow, (x, y))

def draw_cookie(x, y):
    # Option 1: Draw with shapes (current method)
    pygame.draw.circle(WIN, ORANGE, (x+10, y+10), 10)
    # Option 2: Use PNG image instead (uncomment when cookie_img is loaded):
    # WIN.blit(cookie_img, (x, y))

# --- PLAYER NAME ---
def get_player_name():
    global player_name
    name = ""
    entering = True
    # Scale opening background to fit screen
    opening_bg_scaled = pygame.transform.scale(opening_bg, (WIDTH, HEIGHT))
    
    while entering:
        WIN.blit(opening_bg_scaled, (0, 0))
        # Only show the name being typed in white
        if name:
            draw_text_centered(name, FONT, WHITE, WIN, HEIGHT//2)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():  # Only proceed if name is not empty
                        entering = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    # Add character to name (limit length)
                    if len(name) < 20 and event.unicode.isprintable():
                        name += event.unicode
    
    player_name = name.strip() if name.strip() else "Player"
    return player_name

# --- SHOW CONTROLS ---
def show_controls():
    # Scale controls background to fit screen
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

# --- LEVEL RECURSION ---
def retry_level(level_func, attempts=level_attempts):
    if attempts == 0:
        main_menu()
        return
    success = level_func()

    if not success:
        if level_func == level3:
            return 'sigma'
        else:
            retry_level(level_func, attempts-1)

# --- LEVEL 1: Obstacle Course ---
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

    # Scale background to fit screen
    bg_level1_scaled = pygame.transform.scale(bg_level1, (WIDTH, HEIGHT))
    
    run = True
    while run:
        clock.tick(30)
        WIN.blit(bg_level1_scaled, (0, 0))
        for plat in platforms:
            # Scale blocks image to fit platform size and blit it
            scaled_block = pygame.transform.scale(lv1_blocks_img, (plat.width, plat.height))
            WIN.blit(scaled_block, (plat.x, plat.y))
        for c in cookies:
            draw_cookie(c.x, c.y)
        draw_stickman(player.x, player.y, BLUE)
        draw_cow(cow.x, cow.y, facing_right=False)  # Flipped cow image
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
            # Play jump sound (uncomment when jump_sound is loaded):
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
                # Play cookie collection sound (uncomment when cookie_sound is loaded):
                # cookie_sound.play()

        if len(cookies) == 0:
            return True

# --- LEVEL 2: Bomb Defusal ---
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

        # Draw wires
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

# --- LEVEL 3: Decision ---
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
                    return True  # continue to next level

# --- LEVEL 4: Red/Green Light ---
def level4():
    countdown()
    player = pygame.Rect(50, HEIGHT - 100, player_size, player_size)
    goal_x = WIDTH - 100

    GREEN_MIN, GREEN_MAX = 3, 5
    RED_MIN, RED_MAX = 2, 3

    run = True
    light = "GREEN"
    time_left = random.randint(GREEN_MIN, GREEN_MAX)
    last_tick = pygame.time.get_ticks()

    cow_x = WIDTH - 200   # right side cow
    cow_y = HEIGHT - 400

    while run:
        dt = (pygame.time.get_ticks() - last_tick) / 1000
        last_tick = pygame.time.get_ticks()
        time_left -= dt

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()

        # MOVEMENT
        if light == "GREEN":
            if keys[pygame.K_RIGHT]:
                player.x += player_speed // 4
                if player.x >= goal_x:
                    return True
        else:
            if keys[pygame.K_RIGHT]:
                return False

        # WARNING
        warning_text = ""
        if light == 'GREEN' and time_left <= 1:
            warning_text = '!!!'

        # LIGHT SWITCH
        if time_left <= 0:
            if light == "GREEN":
                light = "RED"
                time_left = random.randint(RED_MIN, RED_MAX)
            else:
                light = "GREEN"
                time_left = random.randint(GREEN_MIN, GREEN_MAX)

        # DRAW
        WIN.fill(WHITE)
        draw_stickman(player.x, player.y, BLUE)

        # Light message
        if light == "GREEN":
            draw_text_centered("GREEN LIGHT!", FONT, GREEN, WIN, 50)
        else:
            draw_text_centered("RED LIGHT!", FONT, RED, WIN, 50)

        # 3-2-1 warning
        if warning_text:
            draw_text_centered(warning_text, BIG_FONT, RED, WIN, 120)

        # DRAW COW (direction depends on light)
        # Green light: cow looks away (facing right, away from player)
        # Red light: cow looks at player (facing left, towards player)
        if light == "GREEN":
            draw_cow(cow_x, cow_y, facing_right=False, size=3)  # Flipped to look away
        else:
            draw_cow(cow_x, cow_y, facing_right=True, size=3)  # Not flipped, looks at player

        pygame.display.update()
        clock.tick(30)

# --- LEVEL 5: Final Standoff ---
def level5():
    countdown()

    # Player
    player = pygame.Rect(100, HEIGHT - 100, player_size, player_size)
    player_y_vel = 0
    gravity = 1
    jump_power = -18
    on_ground = True

    # Cow enemy
    cow = pygame.Rect(WIDTH - 150, HEIGHT, player_size, player_size)
    cow_direction = -1      # start moving upward
    cow_speed = 3
    cow_lives = 3
    cow_shoot_timer = 0     # cooldown timer

    # Bullets
    bullets_player = []
    bullets_cow = []

    run = True

    while run:
        dt = clock.tick(30)
        WIN.fill(WHITE)

        # -------------------------------------
        # PLAYER MOVEMENT (JUMP + GRAVITY)
        # -------------------------------------
        keys = pygame.key.get_pressed()

        # Jump
        if keys[pygame.K_UP] and on_ground:
            player_y_vel = jump_power
            on_ground = False

        # Apply gravity
        player_y_vel += gravity
        player.y += player_y_vel

        # Floor collision
        if player.y >= HEIGHT - 100:
            player.y = HEIGHT - 100
            player_y_vel = 0
            on_ground = True

        # -------------------------------------
        # COW MOVEMENT (UP-DOWN)
        # -------------------------------------
        cow.y += cow_direction * cow_speed

        # Bounce when reaching limits
        lowerlim = random.randint(200,300)
        upperlim = random.randint(50,100)
        if cow.y < lowerlim:
            cow.y = lowerlim
            cow_direction = 1
        elif cow.y > HEIGHT-upperlim:
            cow.y = HEIGHT-upperlim
            cow_direction = -1

        # -------------------------------------
        # COW SHOOTING LOGIC
        # -------------------------------------

        cow_shoot_timer -= 1*(1+(4-cow_lives)//5)
        if cow_shoot_timer <= 0:
            # Cow fires at random intervals
            bullets_cow.append([cow.x, cow.y + 20])
            cow_shoot_timer = random.randint(40, 60)  # fire every 1.3–2 sec

        # -------------------------------------
        # DRAW ENTITIES
        # -------------------------------------
        draw_stickman(player.x, player.y, BLUE)
        draw_cow(cow.x, cow.y)
        draw_text_centered("Press SPACE to shoot the cow | UP to jump", FONT, BLACK, WIN, 40)

        # -------------------------------------
        # UPDATE PLAYER BULLETS
        # -------------------------------------
        for b in bullets_player[:]:
            # Draw bullet
            pygame.draw.circle(WIN, RED, (b[0], b[1]), 5)

            # Move bullet
            b[0] += 12

            # Remove if off-screen
            if b[0] > WIDTH:
                bullets_player.remove(b)
                continue

            # Collision with cow
            if cow.collidepoint(b[0], b[1]):
                bullets_player.remove(b)

                cow_lives -= 1  # reduce life

                if cow_lives <= 0:
                    WIN.fill(WHITE)
                    draw_text_centered("You win! Steak and milk!", BIG_FONT, GREEN, WIN, HEIGHT // 2)
                    pygame.display.update()
                    time.sleep(3)
                    return True

        # -------------------------------------
        # UPDATE COW BULLETS
        # -------------------------------------
        for cb in bullets_cow[:]:
            pygame.draw.circle(WIN, PINK, (cb[0], cb[1]), 5)
            cb[0] -= 10

            # remove if off-screen
            if cb[0] < 0:
                bullets_cow.remove(cb)

            # player hit?
            if player.collidepoint(cb[0], cb[1]):
                WIN.fill(WHITE)
                draw_text_centered("You were milk-blasted!", BIG_FONT, PINK, WIN, HEIGHT//2)
                pygame.display.update()
                time.sleep(3)
                return False

        pygame.display.update()

        # -------------------------------------
        # EVENTS
        # -------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Player shoots
                    bullets_player.append([player.x + 20, player.y + 20])
                    # Play shoot sound (uncomment when shoot_sound is loaded):
                    # shoot_sound.play()


# --- MAIN MENU ---
def main_menu():
    # Start background music (uncomment when background music is loaded):
    # pygame.mixer.music.play(-1)  # -1 loops forever
    
    player_name = get_player_name()
    # Show controls page after name entry
    show_controls()
    retry_level(level1)
    retry_level(level2)
    if retry_level(level3) != 'sigma':
        retry_level(level4)
    retry_level(level5)

    WIN.fill(WHITE)
    draw_text_centered("Congratulations! Game Complete!", BIG_FONT, GREEN, WIN, HEIGHT//2)
    pygame.display.update()
    time.sleep(5)
    pygame.quit()
    sys.exit()

main_menu()
