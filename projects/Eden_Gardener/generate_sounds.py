
import wave
import math
import random
import struct
import os

SOUND_DIR = "src/assets/sounds"
os.makedirs(SOUND_DIR, exist_ok=True)

def generate_watering_sound(filename, duration=0.6):
    """Generate white noise with fade in/out to simulate water pouring."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            # White noise
            noise = random.uniform(-1, 1)
            
            # Envelope (Fade In/Out)
            t = i / n_samples
            if t < 0.2:
                envelope = t * 5
            elif t > 0.8:
                envelope = (1 - t) * 5
            else:
                envelope = 1.0
                
            # Volume and scaling
            sample = int(noise * envelope * 8000) # Slightly softer (10000 -> 8000)
            data.append(struct.pack('<h', sample))
            
        wav_file.writeframes(b''.join(data))
    print(f"Generated: {filename}")

def generate_success_sound(filename):
    """Generate a simple major chord arpeggio (C-E-G)."""
    sample_rate = 44100
    duration = 1.0
    n_samples = int(sample_rate * duration)
    
    notes = [523.25, 659.25, 783.99] # C5, E5, G5
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        data = []
        for i in range(n_samples):
            t = i / sample_rate
            value = 0
            
            for j, freq in enumerate(notes):
                # Staggered entry (arpeggio)
                start_time = j * 0.1
                if t >= start_time:
                    # Sine wave
                    local_t = t - start_time
                    decay = math.exp(-local_t * 5)
                    value += math.sin(2 * math.pi * freq * local_t) * decay
            
            # Clipping protection and scaling
            value = max(min(value * 0.3, 1), -1)
            sample = int(value * 20000)
            data.append(struct.pack('<h', sample))
            
        wav_file.writeframes(b''.join(data))
    print(f"Generated: {filename}")

if __name__ == "__main__":
    generate_watering_sound(os.path.join(SOUND_DIR, "water.mp3")) 
    generate_success_sound(os.path.join(SOUND_DIR, "success.mp3"))
