import pygame
import sys
import random
import time
from PIL import Image

# Try to import cv2 for video playback, if not available, skip video
try:
    import cv2
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    print("Warning: opencv-python not installed. Video playback disabled.")

pygame.init()
# Initialize mixer for audio playback
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Basic setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Cow Chase Adventure")

# Dictionary to store color RGB values
# Dictionaries use key-value pairs: {key: value}
# Example: "WHITE" is the key, (255, 255, 255) is the value
# You access values using: COLOR_DICT["WHITE"]
COLOR_DICT = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "ORANGE": (255, 165, 0),
    "PURPLE": (128, 0, 128),
    "BROWN": (139, 69, 19),
    "PINK": (170, 51, 106),
    "CYAN": (0, 255, 255)
}

# Extract colors from dictionary for backwards compatibility
# This allows existing code to still use WHITE, BLACK, etc.
WHITE = COLOR_DICT["WHITE"]
BLACK = COLOR_DICT["BLACK"]
RED = COLOR_DICT["RED"]
GREEN = COLOR_DICT["GREEN"]
BLUE = COLOR_DICT["BLUE"]
YELLOW = COLOR_DICT["YELLOW"]
ORANGE = COLOR_DICT["ORANGE"]
PURPLE = COLOR_DICT["PURPLE"]
BROWN = COLOR_DICT["BROWN"]
PINK = COLOR_DICT["PINK"]
CYAN = COLOR_DICT["CYAN"]

FONT = pygame.font.Font("pixelfont2.otf", 30)
BIG_FONT = pygame.font.Font("pixelfont2.otf", 50)
OUTPIXEL_FONT = pygame.font.Font("pixelfont.otf", 50)

clock = pygame.time.Clock()

player_size = 70
player_speed = 5
jump_strength = 15
gravity = 1
cow_speed = 3
level_attempts = 3
player_name = "Player"
player_health = 3  # Global health tracker (starts with 3 lives)
max_health = 3  # Maximum health value

# Initial loading
cow_img = pygame.image.load("Cow_cartoon_04.svg.png").convert_alpha()
cow_img_original = cow_img.copy()
loading_bg = pygame.image.load("loadingscreen.jfif").convert()
bg_level1 = pygame.image.load("bglevel1.jpeg").convert()
bg_level2 = pygame.image.load("WhatsApp Image 2025-11-22 at 5.21.24 PM.jpeg").convert()
bg_level3 = pygame.image.load('choices.jfif').convert()
bg_level4 = pygame.image.load('WhatsApp Image 2025-11-22 at 5.58.58 PM.jfif').convert()
bg_level5 = pygame.image.load('final.jfif').convert()
lv1_blocks_img = pygame.image.load("lv1blocks.jpeg").convert_alpha()
opening_bg = pygame.image.load("openingpage.jpeg").convert()
controls_bg = pygame.image.load("WhatsApp Image 2025-11-19 at 00.04.47.jpeg").convert()
# cookie_img = pygame.image.load("images/cookie.png").convert_alpha()

# Bullet images for level 5
bullet_size = 25  # Increased from 10
player_bullet_img = pygame.image.load("stickmanblast.png").convert_alpha()
player_bullet_img = pygame.transform.scale(player_bullet_img, (bullet_size, bullet_size))
cow_bullet_img = pygame.image.load("milkblastcow.jpg").convert_alpha()
cow_bullet_img = pygame.transform.scale(cow_bullet_img, (bullet_size, bullet_size))

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

def draw_health_bar(current_health, max_health):
    """
    Draw a health bar in the top right corner
    Shows a black box with diagonal line divisions and red fill
    Health decreases from right to left
    """
    # Health bar dimensions and position
    bar_width = 150
    bar_height = 30
    bar_x = WIDTH - bar_width - 10  # 10 pixels from right edge
    bar_y = 10  # 10 pixels from top
    
    # Draw black background box
    pygame.draw.rect(WIN, BLACK, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(WIN, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)  # White border
    
    # Number of health segments (3 segments for 3 lives)
    num_segments = max_health
    segment_width = bar_width / num_segments
    
    # Draw diagonal division lines between segments
    for i in range(1, num_segments):
        x_pos = bar_x + (i * segment_width)
        # Draw diagonal line from top-left to bottom-right
        pygame.draw.line(WIN, WHITE, (x_pos, bar_y), (x_pos + 3, bar_y + bar_height), 2)
        # Draw diagonal line from bottom-left to top-right
        pygame.draw.line(WIN, WHITE, (x_pos, bar_y + bar_height), (x_pos + 3, bar_y), 2)
    
    # Fill health segments with red (from left to right, up to current_health)
    # Fill decreases from right to left as health decreases
    filled_segments = current_health
    for i in range(filled_segments):
        segment_x = bar_x + (i * segment_width) + 2  # +2 for small padding
        segment_rect = pygame.Rect(segment_x, bar_y + 2, segment_width - 4, bar_height - 4)
        pygame.draw.rect(WIN, RED, segment_rect)

def countdown():
    loadingscr = pygame.transform.scale(loading_bg, (WIDTH, HEIGHT))
    for i in range(3, 0, -1):
        WIN.blit(loadingscr, (0,0))
        draw_text_centered(f"Going in {i}...", OUTPIXEL_FONT, BLACK, WIN, HEIGHT//1.2)
        pygame.display.update()
        time.sleep(0.67)

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
        name_font = pygame.font.Font("pixelfont2.otf", 20)
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
            draw_text_centered(name, OUTPIXEL_FONT, BLACK, WIN, HEIGHT//2)
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

def show_game_over():
    """
    Display game over screen with lose image when player runs out of health
    """
    try:
        lose_img = pygame.image.load("loseimage.jpeg").convert()
        lose_img_scaled = pygame.transform.scale(lose_img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Warning: Could not load lose image: {e}")
        lose_img_scaled = None
    
    # Stop any playing music
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    showing = True
    while showing:
        if lose_img_scaled:
            WIN.blit(lose_img_scaled, (0, 0))
        else:
            WIN.fill(BLACK)
            draw_text_centered("Game Over!", BIG_FONT, RED, WIN, HEIGHT//2 - 30)
            draw_text_centered("You ran out of health!", FONT, WHITE, WIN, HEIGHT//2 + 20)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                showing = False
                break
        clock.tick(30)
    
    # Wait a moment before exiting
    time.sleep(1)
    pygame.quit()
    sys.exit()

def show_game_over():
    """
    Display game over screen with lose image when player runs out of health
    """
    try:
        lose_img = pygame.image.load("loseimage.jpeg").convert()
        lose_img_scaled = pygame.transform.scale(lose_img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Warning: Could not load lose image: {e}")
        lose_img_scaled = None
    
    # Stop any playing music
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    showing = True
    while showing:
        if lose_img_scaled:
            WIN.blit(lose_img_scaled, (0, 0))
        else:
            WIN.fill(BLACK)
            draw_text_centered("Game Over!", BIG_FONT, RED, WIN, HEIGHT//2 - 30)
            draw_text_centered("You ran out of health!", FONT, WHITE, WIN, HEIGHT//2 + 20)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                showing = False
                break
        clock.tick(30)
    
    # Wait a moment before exiting
    time.sleep(1)
    pygame.quit()
    sys.exit()

def play_opening_scene(video_path="openingscenevideo.mp4", audio_path="openingscenevideo.mp3"):
    """
    Play opening scene video before level 1 with audio
    Uses OpenCV to read video frames and pygame.mixer to play audio from separate MP3 file
    """
    # Check if cv2 is available (runtime check, not just import time)
    try:
        import cv2
        cv2_available = True
    except ImportError:
        cv2_available = False
    
    # If cv2 is not available, skip video playback
    if not cv2_available:
        print("OpenCV not available - skipping opening scene video")
        print("Install with: pip install opencv-python")
        # Show a message on screen that video is unavailable
        WIN.fill(BLACK)
        draw_text_centered("Video unavailable", FONT, WHITE, WIN, HEIGHT//2 - 20)
        draw_text_centered("Press any key to continue", FONT, WHITE, WIN, HEIGHT//2 + 20)
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False
                    break
            clock.tick(30)
        return
    
    try:
        # Open video file using OpenCV (cv2 already imported above)
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Warning: Could not open video file: {video_path}")
            print(f"Make sure the file exists in the current directory")
            # Show error message on screen
            WIN.fill(BLACK)
            draw_text_centered("Video file not found", FONT, RED, WIN, HEIGHT//2 - 20)
            draw_text_centered(f"Looking for: {video_path}", 
                             pygame.font.Font("pixelfont2.otf", 20), 
                             WHITE, WIN, HEIGHT//2 + 10)
            draw_text_centered("Press any key to continue", 
                             FONT, WHITE, WIN, HEIGHT//2 + 40)
            pygame.display.update()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                        break
                clock.tick(30)
            return
        
        print(f"Playing opening scene video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30  # Default to 30 FPS if can't read
        
        # Get video duration for audio syncing
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = frame_count / fps if fps > 0 else 0
        
        frame_delay = 1.0 / fps  # Calculate time per frame
        
        # Load and play audio from separate MP3 file
        audio_loaded = False
        import os
        
        # Check if audio file exists
        if os.path.exists(audio_path):
            try:
                print(f"Loading audio file: {audio_path}")
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.set_volume(1.0)  # Full volume
                audio_loaded = True
                print("Audio loaded successfully!")
            except Exception as e:
                print(f"Warning: Could not load audio file: {e}")
                audio_loaded = False
        else:
            print(f"Warning: Audio file not found: {audio_path}")
            print("Video will play without audio")
        
        playing = True
        
        # Start audio playback when video starts (right before first frame)
        if audio_loaded:
            try:
                print("Starting audio playback...")
                pygame.mixer.music.play()
                
                # Give mixer a moment to start
                pygame.time.wait(10)
                
                if pygame.mixer.music.get_busy():
                    print("✓ Audio playback started successfully!")
                else:
                    print("WARNING: Audio not playing. Trying again...")
                    pygame.mixer.music.set_volume(1.0)
                    pygame.mixer.music.play()
                    pygame.time.wait(50)
                    if pygame.mixer.music.get_busy():
                        print("✓ Audio started on second attempt!")
            except Exception as e:
                print(f"ERROR: Could not start audio playback: {e}")
                import traceback
                traceback.print_exc()
        
        while playing:
            ret, frame = cap.read()  # Read next frame
            
            if not ret:  # End of video
                break
            
            # Convert BGR (OpenCV default) to RGB (pygame uses RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to match game window size
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            
            # Convert numpy array to PIL Image, then to pygame surface
            # This method is more reliable than direct numpy conversion
            frame_pil = Image.fromarray(frame_resized)
            # Use frombytes for newer pygame versions, fromstring for older
            try:
                frame_surface = pygame.image.frombytes(
                    frame_pil.tobytes(), 
                    frame_pil.size, 
                    frame_pil.mode
                ).convert()
            except AttributeError:
                # Fallback for older pygame versions
                frame_surface = pygame.image.fromstring(
                    frame_pil.tobytes(), 
                    frame_pil.size, 
                    frame_pil.mode
                ).convert()
            
            # Display frame on screen
            WIN.blit(frame_surface, (0, 0))
            pygame.display.update()
            
            # Control playback speed to match video FPS
            # Cap at reasonable FPS to prevent video from playing too fast
            target_fps = max(min(fps, 60), 10)  # Between 10 and 60 FPS
            clock.tick(target_fps)
            
            # Check for quit events or skip button
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                # Allow user to skip video by pressing any key
                if event.type == pygame.KEYDOWN:
                    print("Video skipped by user")
                    playing = False
                    # Stop audio if playing
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    break
        
        cap.release()  # Release video file
        
        # Wait for audio to finish if it's still playing
        if audio_loaded and pygame.mixer.music.get_busy():
            print("Waiting for audio to finish...")
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)  # Wait 100ms at a time
        
        print("Opening scene video finished")
        # Brief pause after video ends
        time.sleep(0.5)
        
    except Exception as e:
        import traceback
        print(f"Error playing opening scene video: {e}")
        traceback.print_exc()
        # Continue game even if video fails

def play_video(video_path, audio_path=None):
    """
    Video playback function with optional synchronized audio
    Plays video file using OpenCV and displays frames in pygame
    If audio_path is not provided, automatically looks for MP3 with same name
    """
    # Check if cv2 is available
    try:
        import cv2
    except ImportError:
        print(f"OpenCV not available - skipping video: {video_path}")
        return
    
    try:
        import os
        
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return
        
        # Auto-detect audio file if not provided
        if audio_path is None:
            # Replace .mp4 extension with .mp3
            audio_path = os.path.splitext(video_path)[0] + ".mp3"
        
        # Load and start audio if available
        audio_loaded = False
        if os.path.exists(audio_path):
            try:
                print(f"Loading audio: {audio_path}")
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.set_volume(1.0)
                audio_loaded = True
                print("Audio loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load audio file: {e}")
                audio_loaded = False
        else:
            print(f"Audio file not found: {audio_path} - video will play without audio")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Could not open video file: {video_path}")
            return
        
        # Get video FPS
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30
        
        # Start audio playback when video starts
        if audio_loaded:
            try:
                pygame.mixer.music.play()
                print("Audio playback started")
            except Exception as e:
                print(f"Warning: Could not start audio playback: {e}")
        
        playing = True
        
        while playing:
            ret, frame = cap.read()
            
            if not ret:  # End of video
                break
            
            # Convert BGR to RGB and resize
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
            
            # Convert to pygame surface
            frame_pil = Image.fromarray(frame_resized)
            try:
                frame_surface = pygame.image.frombytes(
                    frame_pil.tobytes(), 
                    frame_pil.size, 
                    frame_pil.mode
                ).convert()
            except AttributeError:
                frame_surface = pygame.image.fromstring(
                    frame_pil.tobytes(), 
                    frame_pil.size, 
                    frame_pil.mode
                ).convert()
            
            # Display frame
            WIN.blit(frame_surface, (0, 0))
            pygame.display.update()
            
            # Control playback speed
            target_fps = max(min(fps, 60), 10)
            clock.tick(target_fps)
            
            # Check for quit or skip
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    playing = False
                    # Stop audio if playing
                    if audio_loaded and pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    break
        
        cap.release()  # Release video file
        
        # Wait for audio to finish if it's still playing
        if audio_loaded and pygame.mixer.music.get_busy():
            print("Waiting for audio to finish...")
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)  # Wait 100ms at a time
        
        time.sleep(0.3)  # Brief pause after video
        
    except Exception as e:
        print(f"Error playing video {video_path}: {e}")
        import traceback
        traceback.print_exc()

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
    global player_health
    countdown()
    
    # Dictionary storing level 1 specific configuration
    # Each key represents a game mechanic, value is its setting
    # Dictionaries help organize related data together
    level1_config = {
        "player_speed_multiplier": 0.85,  # 15% speed reduction
        "cow_speed_x": 1.8,  # Horizontal cow movement multiplier
        "cow_speed_y_up": 0.9,  # Vertical cow speed when moving up
        "cow_speed_y_down": 0.9,  # Vertical cow speed when moving down
        "cow_speed_x_backward": 1.5  # Cow speed when moving backward
    }
    
    # Access dictionary values using square brackets: level1_config["key"]
    level1_player_speed = player_speed * level1_config["player_speed_multiplier"]
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
        # Draw health bar
        draw_health_bar(player_health, max_health)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= level1_player_speed
        if keys[pygame.K_RIGHT]:
            player.x += level1_player_speed
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

        # Use dictionary values to control cow movement speed
        # Dictionaries make it easy to adjust values in one place
        if cow.x < player.x:
            cow.x += cow_speed * level1_config["cow_speed_x"]
        elif cow.x > player.x:
            cow.x -= cow_speed * level1_config["cow_speed_x_backward"]
        if cow.y < player.y:
            cow.y += cow_speed * level1_config["cow_speed_y_up"]
        elif cow.y > player.y:
            cow.y -= cow_speed * level1_config["cow_speed_y_down"]
        if player.colliderect(cow):
            player_health -= 1
            # Check if health is depleted
            if player_health <= 0:
                show_game_over()
            return False

        for c in cookies[:]:
            # Smaller hitbox for cookies (14x14 instead of 20x20)
            cookie_hitbox = pygame.Rect(c.x + 3, c.y + 3, 14, 14)
            if player.colliderect(cookie_hitbox):
                cookies.remove(c)
                # cookie_sound.play()

        if len(cookies) == 0:
            return True

def level2():
    global player_health
    # Play video before bomb round (level 2)
    play_video("beforebombvideo.mp4")
    countdown()
    rainbow_wires = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    wire_order = rainbow_wires.copy()
    random.shuffle(rainbow_wires)
    drawn_order = []

    # Dictionary mapping keyboard keys to wire indices (0-6)
    # Each pygame key constant maps directly to a wire position
    # Access with: key_to_wire_index[pygame.K_1] returns 0
    key_to_wire_index = {
        pygame.K_1: 0,   # Key 1 on main keyboard -> wire index 0
        pygame.K_KP1: 0, # Key 1 on numpad -> wire index 0
        pygame.K_2: 1,   # Key 2 on main keyboard -> wire index 1
        pygame.K_KP2: 1, # Key 2 on numpad -> wire index 1
        pygame.K_3: 2,   # Key 3 on main keyboard -> wire index 2
        pygame.K_KP3: 2, # Key 3 on numpad -> wire index 2
        pygame.K_4: 3,   # Key 4 on main keyboard -> wire index 3
        pygame.K_KP4: 3, # Key 4 on numpad -> wire index 3
        pygame.K_5: 4,   # Key 5 on main keyboard -> wire index 4
        pygame.K_KP5: 4, # Key 5 on numpad -> wire index 4
        pygame.K_6: 5,   # Key 6 on main keyboard -> wire index 5
        pygame.K_KP6: 5, # Key 6 on numpad -> wire index 5
        pygame.K_7: 6,   # Key 7 on main keyboard -> wire index 6
        pygame.K_KP7: 6  # Key 7 on numpad -> wire index 6
    }

    bg_level2_scaled = pygame.transform.scale(bg_level2, (WIDTH, HEIGHT))

    run = True
    while run:
        WIN.blit(bg_level2_scaled, (0, 0))

        for i, color in enumerate(rainbow_wires):
            rect = pygame.Rect(155+i*80, HEIGHT//2, 20, 1000)
            pygame.draw.rect(WIN, pygame.Color(color), rect)
        draw_text_centered(' 1       2       3       4       5       6       7',
                           FONT, WHITE, WIN, HEIGHT//2 - 35)

        draw_text_centered(f"Cut sequence: {drawn_order}",
                           pygame.font.Font("pixelfont2.otf", 20), WHITE, WIN, HEIGHT//4+15)
        
        # Draw health bar
        draw_health_bar(player_health, max_health)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Use dictionary to lookup wire index for pressed key
                # .get() method safely returns None if key doesn't exist
                # This prevents errors if player presses wrong key
                idx = key_to_wire_index.get(event.key)
                
                # If a valid key was pressed (idx is not None)
                if idx is not None:
                    drawn_order.append(rainbow_wires[idx])
                    if drawn_order != wire_order[:len(drawn_order)]:
                        player_health -= 1
                        # Check if health is depleted
                        if player_health <= 0:
                            show_game_over()
                        draw_text_centered("BOOM! Wrong wire!", BIG_FONT, RED, WIN, HEIGHT//2)
                        pygame.display.update()
                        time.sleep(2)
                        return False
                    if drawn_order == wire_order:
                        return True

def level3():
    # Play video before decision round (level 3)
    play_video("beforedecisionvideo.mp4")
    countdown()
    bg_level3_scaled = pygame.transform.scale(bg_level3, (WIDTH, HEIGHT))
    run = True
    while run:
        WIN.blit(bg_level3_scaled,(0,0))
        draw_text_centered(f"{'  '*26}B: Give milk back", pygame.font.Font("pixelfont2.otf", 28), GREEN, WIN, HEIGHT//3+15)
        draw_text_centered(f"A: Run away{'  '*25}", FONT, RED, WIN, HEIGHT//3+7)
        # Draw health bar
        draw_health_bar(player_health, max_health)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    # Play video when user chooses option B
                    play_video("userchooseoptionBvideo.mp4")
                    # Play aftergamewinvideo after user chooses option B
                    play_video("aftergamewinvideo.mp4")
                    return False
                elif event.key == pygame.K_a:
                    return True

def level4():
    global player_health
    # Play video before red light/green light round (level 4)
    play_video("redlightgreenlight.mp4")
    countdown()
    player = pygame.Rect(50, HEIGHT - 100, player_size, player_size)
    goal_x = WIDTH - 100

    # Dictionary storing timing ranges for each light state
    # Nested dictionaries: each light state has min/max timing values
    # Structure: {"LIGHT_STATE": {"min": value, "max": value}}
    light_timing = {
        "GREEN": {"min": 3, "max": 5},  # Green light lasts 3-5 seconds
        "RED": {"min": 2, "max": 3}     # Red light lasts 2-3 seconds
    }

    run = True
    light = "GREEN"
    # Access nested dictionary: light_timing["GREEN"]["min"] gets minimum value
    time_left = random.randint(light_timing["GREEN"]["min"], 
                               light_timing["GREEN"]["max"])
    last_tick = pygame.time.get_ticks()

    bg_level4_scaled = pygame.transform.scale(bg_level4, (WIDTH, HEIGHT))

    cow_x = WIDTH - 220
    cow_y = HEIGHT - 400

    while run:
        WIN.blit(bg_level4_scaled, (0,0))
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
                player.x += player_speed // 2.5
                if player.x >= goal_x:
                    return True
        else:
            if keys[pygame.K_RIGHT]:
                player_health -= 1
                # Check if health is depleted
                if player_health <= 0:
                    show_game_over()
                return False

        warning_text = ""
        if light == 'GREEN' and time_left <= 1:
            warning_text = '!!!'

        if time_left <= 0:
            # Switch light state and get new timing from dictionary
            if light == "GREEN":
                light = "RED"
                # Use current light state to get timing from dictionary
                time_left = random.randint(light_timing[light]["min"], 
                                         light_timing[light]["max"])
            else:
                light = "GREEN"
                time_left = random.randint(light_timing[light]["min"], 
                                         light_timing[light]["max"])

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
        
        # Draw health bar
        draw_health_bar(player_health, max_health)

        pygame.display.update()
        clock.tick(30)

def level5():
    global player_size, player_health
    # Play video before last level (level 5)
    play_video("beforelastlevel.mp4")
    countdown()
    
    # Load milkblasted image for death screen
    try:
        milkblasted_img = pygame.image.load("milkblasted.jpeg").convert()
        milkblasted_img_scaled = pygame.transform.scale(milkblasted_img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Warning: Could not load milkblasted image: {e}")
        milkblasted_img_scaled = None
    
    # Load and start looping background music for final round
    import os
    audio_loaded = False
    if os.path.exists("finalround.mp3"):
        try:
            print("Loading final round music...")
            pygame.mixer.music.load("finalround.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)  # -1 means loop forever
            audio_loaded = True
            print("Final round music started (looping)")
        except Exception as e:
            print(f"Warning: Could not load final round music: {e}")

    # Dictionary storing all level 5 game settings
    # Dictionaries are great for organizing related configuration data
    level5_settings = {
        "player_size_multiplier": 1.3,      # Player is 30% larger
        "cow_size_multiplier": 1.4,         # Cow is 40% larger
        "base_cow_width": 75,               # Base cow image width
        "base_cow_height": 50,              # Base cow image height
        "gravity": 1,                       # Downward acceleration
        "jump_power": -18,                  # Upward velocity when jumping
        "cooldown_duration": 500,           # Milliseconds between shots
        "cow_speed": 3,                     # Cow movement speed
        "cow_lives": 3,                     # Number of hits to defeat cow
        "bullet_speed_player": 12,          # Player bullet speed (right)
        "bullet_speed_cow": 10,             # Cow bullet speed (left)
        "cow_shoot_min": 40,                # Min frames between cow shots
        "cow_shoot_max": 60                 # Max frames between cow shots
    }
    
    # Calculate sizes using dictionary values
    level5_player_size = int(player_size * level5_settings["player_size_multiplier"])
    level5_cow_size = level5_settings["cow_size_multiplier"]
    
    player = pygame.Rect(100, HEIGHT - 100, level5_player_size, level5_player_size)
    player_y_vel = 0
    gravity = level5_settings["gravity"]
    jump_power = level5_settings["jump_power"]
    cooldown_duration = level5_settings["cooldown_duration"]
    last_key_press_time = 0
    on_ground = True

    # Use dictionary values to calculate cow dimensions
    cow = pygame.Rect(WIDTH - 150, HEIGHT, 
                     int(level5_settings["base_cow_width"] * level5_cow_size), 
                     int(level5_settings["base_cow_height"] * level5_cow_size))
    cow_direction = -1
    cow_speed = level5_settings["cow_speed"]
    cow_lives = level5_settings["cow_lives"]
    cow_shoot_timer = 0
    bullets_player = []  # Will store [x, y] positions
    bullets_cow = []  # Will store [x, y] positions

    bg_level5_scaled = pygame.transform.scale(bg_level5, (WIDTH, HEIGHT))

    run = True

    while run:
        dt = clock.tick(30)
        current_time = pygame.time.get_ticks()
        WIN.blit(bg_level5_scaled, (0,0))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and on_ground:
            # Use dictionary value for jump power
            player_y_vel = level5_settings["jump_power"]
            on_ground = False

        # Use dictionary value for gravity
        player_y_vel += level5_settings["gravity"]
        player.y += player_y_vel

        # Ground collision - adjust for larger player size
        ground_level = HEIGHT - 100
        if player.y + level5_player_size >= ground_level:
            player.y = ground_level - level5_player_size
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
            bullets_cow.append([cow.x, 
                              cow.y + int(level5_settings["base_cow_height"] * 
                                        level5_cow_size // 2)])
            # Use dictionary values for shoot timing range
            cow_shoot_timer = random.randint(
                level5_settings["cow_shoot_min"], 
                level5_settings["cow_shoot_max"]
            )

        # Draw player with increased size
        original_player_size = player_size
        player_size = level5_player_size
        draw_stickman(player.x, player.y, BLUE)
        player_size = original_player_size
        
        draw_cow(cow.x, cow.y, size=level5_cow_size)
        draw_text_centered("Press SPACE to shoot the cow | UP to jump", FONT, BLACK, WIN, 40)
        
        for b in bullets_player[:]:
            bullet_x = b[0] - bullet_size // 2
            bullet_y = b[1] - bullet_size // 2
            WIN.blit(player_bullet_img, (bullet_x, bullet_y))

            # Use dictionary value for player bullet speed
            b[0] += level5_settings["bullet_speed_player"]
            if b[0] > WIDTH:
                bullets_player.remove(b)
                continue

            # Proper hitbox matching bullet image size
            bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_size, bullet_size)
            if cow.colliderect(bullet_rect):
                bullets_player.remove(b)
                cow_lives -= 1
                if cow_lives <= 0:
                    # Stop the looping music
                    if audio_loaded:
                        pygame.mixer.music.stop()
                    # Play video after winning the game (replaces text message)
                    play_video("aftergamewinvideo.mp4")
                    return True

        for cb in bullets_cow[:]:
            # Reduced circle size for final round bullets
            circle_radius = 8  # Smaller circle (16 pixels diameter)
            circle_center_x = int(cb[0])
            circle_center_y = int(cb[1])
            
            # Draw white circle instead of milkblast image
            pygame.draw.circle(WIN, WHITE, 
                             (circle_center_x, circle_center_y), 
                             circle_radius)
            
            # Use dictionary value for cow bullet speed (moving left)
            cb[0] -= level5_settings["bullet_speed_cow"]
            if cb[0] < 0:
                bullets_cow.remove(cb)
                continue
            
            # Hitbox matches circle size perfectly (circle diameter = 2 * radius)
            circle_diameter = circle_radius * 2
            bullet_rect = pygame.Rect(
                circle_center_x - circle_radius, 
                circle_center_y - circle_radius, 
                circle_diameter, 
                circle_diameter
            )
            if player.colliderect(bullet_rect):
                # Stop the looping music
                if audio_loaded:
                    pygame.mixer.music.stop()
                player_health -= 1
                # Check if health is depleted
                if player_health <= 0:
                    show_game_over()
                # Show milkblasted image instead of text message
                if milkblasted_img_scaled:
                    WIN.blit(milkblasted_img_scaled, (0, 0))
                else:
                    WIN.fill(WHITE)
                    draw_text_centered("You were milk-blasted!", BIG_FONT, PINK, WIN, HEIGHT//2)
                pygame.display.update()
                time.sleep(3)
                return False
        
        # Draw health bar last so it appears on top
        draw_health_bar(player_health, max_health)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Stop music before quitting
                if audio_loaded:
                    pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Use dictionary value for cooldown duration
                    if (current_time - last_key_press_time >= 
                        level5_settings["cooldown_duration"]):
                        bullets_player.append([player.x + level5_player_size // 2, 
                                             player.y + level5_player_size // 2])
                        last_key_press_time = current_time
                    # shoot_sound.play()


# menus
def main_menu():
    # pygame.mixer.music.play(-1)  # -1 loops forever
    # Reset player health at the start of the game
    global player_health
    player_health = max_health
    
    player_name = get_player_name()
    show_controls()
    # Play opening scene video before starting level 1
    play_opening_scene()
    retry_level(level1)
    retry_level(level2)
    if retry_level(level3) != 'good ending':
        retry_level(level4)
        retry_level(level5)

    # After completing all levels, the aftergamewinvideo already played in level 5
    # No need to show congratulations message - video handles it
    pygame.quit()
    sys.exit()

main_menu()