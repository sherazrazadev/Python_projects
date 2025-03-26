import pygame
from pygame.locals import QUIT
import pyaudio
import numpy as np

# Initialization
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Loudness Awareness Game")
font = pygame.font.Font(None, 30) 

# Audio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Constants 
LOUDNESS_MAX = 31000  # Adjust if needed for your microphone
LOUDNESS_MIN = 14000   # Adjust if needed 
METER_WIDTH = 200
METER_HEIGHT = 50
METER_X = (width - METER_WIDTH) // 2
METER_Y = height - METER_HEIGHT - 50

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_meter(loudness):
    # Normalize loudness for meter scaling
    normalized_loudness = (loudness - LOUDNESS_MIN) / (LOUDNESS_MAX - LOUDNESS_MIN) 
    filled_width = int(normalized_loudness * METER_WIDTH)

    # Meter background
    pygame.draw.rect(screen, (150, 150, 150), (METER_X, METER_Y, METER_WIDTH, METER_HEIGHT), 2)

    # Filled meter (clamp width to avoid exceeding the frame)
    filled_width = min(int(normalized_loudness * METER_WIDTH), METER_WIDTH)
    pygame.draw.rect(screen, (0, 200, 0), (METER_X, METER_Y, filled_width, METER_HEIGHT))

    # Meter labels
    draw_text("Low", (0, 0, 0), METER_X - 50, METER_Y + 15)
    draw_text("High", (0, 0, 0), METER_X + METER_WIDTH + 5, METER_Y + 15)

def draw_volume_feedback(loudness):
    if loudness > LOUDNESS_MAX:
        feedback_text = "High Volume!"
        color = (255, 0, 0)  # Red
    elif loudness < LOUDNESS_MIN:
        feedback_text = "Low Volume"
        color = (0, 0, 255)  # Blue
    else:
        feedback_text = "Normal Volume"
        color = (0, 128, 0)  # Green

    draw_text(feedback_text, color, width // 2 - 100, 50)
def loudness_awareness_game():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
        data = stream.read(CHUNK)
        audio_chunk = np.frombuffer(data, dtype=np.int16)
        loudness = np.max(np.abs(audio_chunk))

        screen.fill((255, 255, 255))  

        # Display Loudness information 
        draw_text(f"Loudness: {loudness}", (0, 0, 0), 50, 100) 

        # Draw the meter
        draw_meter(loudness) 

        # Draw Volume Feedback
        draw_volume_feedback(loudness)

        pygame.display.flip()

if __name__ == "__main__":
    loudness_awareness_game()

# **Explanation:**

# 1. **Constants:** Sets up constants for the loudness range and meter dimensions.
# 2. **`draw_meter` Function:** Takes the loudness value, normalizes it, calculates the width of the filled meter, and draws the meter with labels.
# 3. **Game Loop:** 
#    * Clears the screen.
#    * Displays loudness value.
#    * Calls `draw_meter` to visualize the loudness level.

# **Remember:** Adjust the `LOUDNESS_MAX` and `LOUDNESS_MIN` constants to match the sensitivity of your microphone.

# Let me know if you have any other UI elements you'd like added or customized! 
