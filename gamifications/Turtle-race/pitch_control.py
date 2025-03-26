import pygame
from pygame.locals import QUIT
from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import Sine
import numpy as np
import pyaudio
import threading

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pitch Correction Game")

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

def generate_reference_pitch():
    # Generate a reference pitch (e.g., A4) as a sine wave
    return Sine(440).to_audio_segment(duration=1000)

def pitch_correction_game():
    reference_pitch = generate_reference_pitch()

    draw_text("Sing along and try to match the reference pitch!", black, 50, height // 2)
    pygame.display.flip()

    play(reference_pitch)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        # Read audio from the microphone
        data = stream.read(CHUNK)
        audio_chunk = AudioSegment(data, frame_rate=RATE, sample_width=2, channels=1)

        # Perform pitch analysis (replace with your pitch analysis code)
        # For simplicity, let's assume a basic pitch analysis that checks if the pitch is close to the reference
        pitch_difference = np.abs(audio_chunk.dBFS - reference_pitch.dBFS)

        # Visualize pitch difference on the screen
        screen.fill(white)
        draw_text(f"Pitch Difference: {pitch_difference:.2f} dB", black, 50, height // 2)
        pygame.display.flip()

        # Adjust the pitch of the user's voice (replace with your pitch correction code)
        # For simplicity, let's assume a basic pitch correction that adjusts the pitch based on the difference
        pitch_correction_factor = 1.0 - pitch_difference / 50.0
        adjusted_audio_chunk = audio_chunk.speedup(playback_speed=pitch_correction_factor)

        # Play the adjusted audio
        play(adjusted_audio_chunk)

if __name__ == "__main__":
    # Set up display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pitch Correction Game")

    pitch_correction_game()
