import numpy as np
import wave

sample_rate = 44100  # Hz
duration = 0.4       # seconds
frequency = 900      # Hz (slightly higher tone than click.wav)

t = np.linspace(0, duration, int(sample_rate * duration), False)
tone = np.sin(frequency * t * 2 * np.pi)

# Fade out effect for a nice "ding"
fade = np.linspace(1, 0, len(tone))
tone = tone * fade

# Normalize to 16-bit
tone = (tone * 32767).astype(np.int16)

with wave.open("answer.wav", "w") as f:
    f.setnchannels(1)       # mono
    f.setsampwidth(2)       # 16-bit
    f.setframerate(sample_rate)
    f.writeframes(tone.tobytes())

print("✅ answer.wav generated successfully!")
