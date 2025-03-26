import pygame
import time
import os
import tempfile
import wave
import pyaudio

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Script Training Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set up fonts and text
font = pygame.font.Font(None, 24)

# Set up PyAudio for recording and playback
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def record_audio(filename, duration=5):
    frames = []

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording...")
    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))


def play_audio(filename):
    sound = pygame.mixer.Sound(filename)
    sound.play()
    pygame.time.delay(int(sound.get_length() * 1000))  # Delay to allow sound playback to finish



def script_training_game():
    scripts = [
        "The quick brown fox jumps over the lazy dog.",
        "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
        "She sells sea shells by the sea shore."
    ]

    current_script_index = 0

    while current_script_index < len(scripts):
        script = scripts[current_script_index]

        print("Script to read:", script)

        audio_filename = os.path.join(tempfile.gettempdir(), f"user_recording_{current_script_index}.wav")

        draw_text("Read the script and press 'R' to record:", black, 50, height // 2)
        pygame.display.flip()

        recording = False

        while True:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_r] and not recording:
                recording = True
                record_audio(audio_filename, duration=5)
                draw_text("Recording complete. Press 'P' to playback or 'Q' to quit.", black, 50, height // 2 + 50)
                pygame.display.flip()

            if keys[pygame.K_p]:
                play_audio(audio_filename)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (keys[pygame.K_q] and not recording):
                    pygame.quit()
                    return

            if not pygame.mixer.music.get_busy() and recording:
                # Verify if the recorded script matches the expected script
                user_audio_filename = audio_filename
                play_audio(user_audio_filename)

                # You should implement a function to check if the user's recording matches the script
                # For simplicity, let's assume it's a perfect match
                is_match = True

                if is_match:
                    current_script_index += 1
                    break
                else:
                    print("Recording does not match the script. Please try again.")
                    recording = False

            pygame.display.flip()

if __name__ == "__main__":
    # Set up display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Script Training Game")

    script_training_game()
