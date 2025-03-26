import pyaudio
import numpy as np
import tkinter as tk

# Function to calculate volume level from audio data
def calculate_volume(data):
    # Convert audio data to numpy array
    audio_data = np.frombuffer(data, dtype=np.int16)
    # Calculate root mean square (RMS) amplitude
    rms = np.sqrt(np.mean(np.square(audio_data)))
    # Normalize RMS amplitude to a range of 0 to 1
    volume = rms / 32768.0
    return volume

# Function to continuously monitor microphone input
def monitor_microphone():
    # Define parameters for audio recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open microphone stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Create GUI window
    root = tk.Tk()
    root.title("Voice Control Game")

    # Label for feedback
    feedback_label = tk.Label(root, text="Speak into the microphone...")
    feedback_label.pack()

    # Function to update feedback label based on volume
    def update_feedback():
        # Read audio data from stream
        data = stream.read(CHUNK)
        # Calculate volume level
        volume = calculate_volume(data)
        # Provide feedback based on volume level
        if volume > 0.1:
            feedback_label.config(text="Too Loud!")
        elif volume < 0.1:
            feedback_label.config(text="Too Low!")
        else:
            feedback_label.config(text="Just Right!")
        # Schedule next update
        root.after(100, update_feedback)

    # Start updating feedback label
    update_feedback()

    # Run GUI main loop
    root.mainloop()

    # Stop stream and close PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

# Start monitoring microphone
monitor_microphone()
