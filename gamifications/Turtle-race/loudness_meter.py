import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE 
import pyaudio
import numpy as np

# Initialization
pygame.init()

# Game Window Setup
game_width, game_height = 400, 600
game_screen = pygame.display.set_mode((game_width, game_height))
pygame.display.set_caption("Loudness Jumping Game")

# Meter/Feedback window 
info_width = 400
info_height = 150
info_screen = pygame.display.set_mode((info_width, info_height)) 
pygame.display.set_caption("Loudness Information")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 128, 0)
red = (255, 0, 0)

# Font
font = pygame.font.Font(None, 30) 

# Audio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Constants 
LOUDNESS_MAX = 35000
LOUDNESS_MIN = 500
LOUDNESS_MID = (LOUDNESS_MAX + LOUDNESS_MIN) // 2  # Middle loudness
METER_WIDTH = 200
METER_HEIGHT = 50
METER_X = (info_width - METER_WIDTH) // 2
METER_Y = info_height - METER_HEIGHT - 50 
PLAYER_SIZE = 50
GRAVITY = 0.5   
JUMP_STRENGTH_NORMAL = 10
JUMP_STRENGTH_HIGH = 15
FLOOR_Y = game_height - PLAYER_SIZE 

# Helper functions
# Helper functions
def draw_text(text, color, x, y, screen):  # Added 'screen' argument
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_meter(loudness, screen):  # Added the 'screen' parameter
    normalized_loudness = (loudness - LOUDNESS_MIN) / (LOUDNESS_MAX - LOUDNESS_MIN) 
    filled_width = min(int(normalized_loudness * METER_WIDTH), METER_WIDTH)

    # Use the 'screen' object passed as an argument
    pygame.draw.rect(screen, (150, 150, 150), (METER_X, METER_Y, METER_WIDTH, METER_HEIGHT), 2) 
    pygame.draw.rect(screen, (0, 200, 0), (METER_X, METER_Y, filled_width, METER_HEIGHT))

    draw_text("Low", black, METER_X - 50, METER_Y + 15, screen) 
    draw_text("High", black, METER_X + METER_WIDTH + 5, METER_Y + 15, screen) 


def draw_volume_feedback(loudness, screen):  # Added 'screen' argument
    if loudness > LOUDNESS_MAX:
        feedback_text = "High Volume!"
        color = (255, 0, 0)  
    elif loudness < LOUDNESS_MIN:
        feedback_text = "Low Volume"
        color = (0, 0, 255)  
    else:
        feedback_text = "Normal Volume"
        color = (0, 128, 0) 

    # Get the width of the screen for centering  
    screen_width = screen.get_width()  

    draw_text(feedback_text, color, screen_width // 2 - 100, 50, screen) 

# Player object

# Player object 
class Player:
    def __init__(self):
        self.x = game_width // 2 - PLAYER_SIZE // 2
        self.rect = pygame.Rect(self.x, FLOOR_Y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity = 0
        self.is_jumping = False  

    def update(self, loudness):
        if self.is_jumping:
            if loudness > LOUDNESS_MID:
                self.velocity -= JUMP_STRENGTH_HIGH  # High Jump
            else:
                self.velocity -= JUMP_STRENGTH_NORMAL  # Normal Jump
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.velocity = 0
            self.is_jumping = False  

    def draw(self):
        pygame.draw.rect(game_screen, blue, self.rect) 
player = Player()


def loudness_awareness_game():
    while True:
        # Event Handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN and event.key == K_SPACE and not player.is_jumping:
                player.is_jumping = True  

        # Audio Handling
        data = stream.read(CHUNK)
        audio_chunk = np.frombuffer(data, dtype=np.int16)
        loudness = np.max(np.abs(audio_chunk))

        # Game Updates
        player.update(loudness)

        # Game Drawing
        game_screen.fill(white)  
        player.draw()  # Draw player first
        pygame.display.flip()

        # Meter and Feedback Drawing
        info_screen.fill(white)
        draw_text(f"Loudness: {loudness}", black, 20, 20, info_screen)
        draw_meter(loudness, info_screen) 
        draw_volume_feedback(loudness, info_screen) 
        pygame.display.update() 

if __name__ == "__main__":
    loudness_awareness_game()
