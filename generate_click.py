# generate_click.py
import numpy as np
import wave

sample_rate = 44100  # Hz
duration = 0.2       # seconds
frequency = 600      # Hz (beep frequency)
t = np.linspace(0, duration, int(sample_rate * duration), False)
tone = np.sin(frequency * t * 2 * np.pi)

# Normalize to 16-bit range
tone = (tone * 32767).astype(np.int16)

# Write to wav file
with wave.open("click.wav", "w") as f:
    f.setnchannels(1)       # mono
    f.setsampwidth(2)       # 2 bytes per sample
    f.setframerate(sample_rate)
    f.writeframes(tone.tobytes())

print("click.wav generated successfully!")
