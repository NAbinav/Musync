import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import scipy.io.wavfile
import os

def record_system_audio(duration, output_file="output.mp3", sample_rate=44100):
    # Set up PulseAudio source to monitor output (manually set in pavucontrol)
    print("Recording system audio... Open pavucontrol and set the input to the monitor of your output device.")
    
    # Record audio
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    # Save as WAV temporarily
    temp_wav = "temp_audio.wav"
    scipy.io.wavfile.write(temp_wav, sample_rate, recording)
    
    # Convert WAV to MP3 using pydub
    audio = AudioSegment.from_wav(temp_wav)
    audio.export(output_file, format="mp3")
    
    # Clean up temporary WAV file
    os.remove(temp_wav)
    print(f"Audio saved as {output_file}")

if __name__ == "__main__":
    # Record for 10 seconds (adjust as needed)
    record_system_audio(duration=10, output_file="system_audio.mp3")
