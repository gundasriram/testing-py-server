import os
import whisper

# Add folders
checkContentFolder = os.path.exists("content")
checkDownLoadFolder = os.path.exists("download")
if not checkContentFolder:
  os.mkdir("content")
if not checkDownLoadFolder:
  os.mkdir("download")


fileName = "audio.mp3"
lang = "en"
model = whisper.load_model("base")

# Load audio
audio = whisper.load_audio(f"content/{fileName}")
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

# Output the recognized text
options = whisper.DecodingOptions(language=lang, without_timestamps=True)
result = whisper.decode(model, mel, options)
print(result.text)

# Write into a text file
with open(f"download/{fileName}.txt", "w") as f:
  f.write(f"▼ Transcription of {fileName}\n")
  f.write(result.text)