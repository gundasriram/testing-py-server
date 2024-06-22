import whisper

fileName = "audio.wav"
lang = "en"
model = whisper.load_model("tiny")

# Load audio
audio = whisper.load_audio(f"audio2.ogg")
# audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

result = model.transcribe(audio)
print(result)