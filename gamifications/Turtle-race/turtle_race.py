import pygame
import time
import speech_recognition as sr

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Turtle and Hare Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set up fonts and text
font = pygame.font.Font(None, 36)

# Initialize speech recognition
recognizer = sr.Recognizer()

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def turtle_and_hare_game():
    turtle_position = 0
    hare_position = 0

    def speak_and_move(character, speed):
        nonlocal turtle_position, hare_position
        pygame.event.pump()
        with sr.Microphone() as source:
            print(f"Say '{character}' slowly and clearly...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            spoken_text = recognizer.recognize_google(audio).lower()
            if spoken_text == character:
                if character == "turtle":
                    turtle_position += speed
                elif character == "hare":
                    hare_position += speed
                return True
        except sr.UnknownValueError:
            pass

        return False

    while turtle_position < width and hare_position < width:
        screen.fill(white)
        draw_text("Say 'turtle' slowly:", black, 50, height // 2)
        pygame.display.flip()

        if speak_and_move("turtle", 5):
            time.sleep(0.5)

        screen.fill(white)
        draw_text("Say 'hare' slowly:", black, 50, height // 2)
        pygame.display.flip()

        if speak_and_move("hare", 10):
            time.sleep(0.5)

    if turtle_position >= width:
        print("Congratulations! The turtle wins!")
    else:
        print("Hurray! The hare wins!")

    pygame.quit()

if __name__ == "__main__":
    turtle_and_hare_game()
