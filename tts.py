from transformers import pipeline
import scipy
import numpy as np
import os

def generate_audio(text):
    synthesiser = pipeline("text-to-speech", "suno/bark-small")
    speech = synthesiser(text, forward_params={"do_sample": True})

    # Sanitize the filename to remove invalid characters
    sanitized_text = "".join(c for c in text[:20] if c.isalnum() or c in (' ', '_')).rstrip()
    audio_path = os.path.join("Final_Video", f"audio_{sanitized_text}.wav")
    
    # Konwersja danych audio na int16
    audio_int16 = np.int16(speech["audio"].squeeze() * 32767)

    # Upewnienie się że dane są jednowymiarowe (mono)
    if audio_int16.ndim > 1:
        audio_int16 = audio_int16.mean(axis=0).astype(np.int16)

    # Sprawdzenie częstotliwości próbkowania
    sampling_rate = speech["sampling_rate"]
    if not (0 < sampling_rate <= 65535):
        sampling_rate = 24000  # domyślna wartość dla Bark

    # Zapisanie pliku WAV
    scipy.io.wavfile.write(audio_path, rate=sampling_rate, data=audio_int16)

    print(f"Audio wygenerowane: {audio_path}")
    return audio_path
