import tkinter as tk
import pyaudio
import numpy as np
import time

CHUNK = 512  # Audio chunk size
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Sample rate

def monitor_voice_volume():
    p = pyaudio.PyAudio()

    def update_volume_feedback():
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        data = stream.read(CHUNK)
        stream.stop_stream()
        stream.close()

        volume_norm = np.linalg.norm(np.frombuffer(data, dtype=np.int16))

        TOO_LOUD_THRESHOLD = 0.08  # Might need adjusting
        TOO_LOW_THRESHOLD = 0.02

        if volume_norm > TOO_LOUD_THRESHOLD:
            feedback_label.config(text="Your voice is too loud!")
        elif volume_norm < TOO_LOW_THRESHOLD:
            feedback_label.config(text="Your voice is too low!")
        else:
            feedback_label.config(text="Your voice volume is normal.")

        root.after(100, update_volume_feedback)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Voice Volume Feedback")

    feedback_label = tk.Label(root, text="Starting...", font=("Arial", 16))
    feedback_label.pack(pady=20)

    monitor_voice_volume()
    
    root.mainloop()
