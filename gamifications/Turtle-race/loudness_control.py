import pygame
from pygame.locals import QUIT
import pyaudio
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Loudness Awareness Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set up fonts and text
font = pygame.font.Font(None, 24)

# Set up PyAudio for microphone input
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def loudness_awareness_game():
    balloon_radius = 50
    balloon_color = white

    draw_text("Blow into the microphone to control the size of the balloon!", black, 50, height // 2)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        # Read audio from the microphone
        data = stream.read(CHUNK)
        audio_chunk = np.frombuffer(data, dtype=np.int16)

        # Calculate the loudness (replace with your loudness calculation code)
        # For simplicity, let's assume loudness is proportional to the amplitude of the audio
        loudness = np.max(np.abs(audio_chunk))

        # Adjust the balloon size based on loudness
        balloon_radius = int(loudness / 100)
        if balloon_radius > 100:
            balloon_radius = 100

        # Visualize loudness on the screen
        screen.fill(white)
        pygame.draw.circle(screen, balloon_color, (width // 2, height // 2), balloon_radius)
        draw_text(f"Loudness: {loudness}", black, 50, height // 2 + 50)
        pygame.display.flip()

if __name__ == "__main__":
    # Set up display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Loudness Awareness Game")

    loudness_awareness_game()
