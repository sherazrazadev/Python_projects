import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from aubio import pitch

# Set up PyAudio
p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Set up Aubio
pDetection = pitch("yin", CHUNK, CHUNK, RATE)
pDetection.set_unit("midi")
pDetection.set_silence(-40)

# Set up Matplotlib
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))

ax.set_ylim(0, 120)  # Adjust the y-axis limit based on your pitch range
ax.set_xlim(0, 2 * CHUNK)  # Adjust the x-axis limit

# Real-time updating loop
try:
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

        # Convert the data to float
        data_float = data.astype(np.float32) / 32768.0

        # Perform pitch analysis
        pitch_value = pDetection(data_float)[0]
        if pitch_value != 0:
            line.set_ydata([pitch_value] * CHUNK)
            ax.set_title(f'Pitch: {pitch_value:.2f} MIDI')

        plt.pause(0.01)

except KeyboardInterrupt:
    pass

# Close the stream when done
stream.stop_stream()
stream.close()
p.terminate()
