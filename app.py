from flask import Flask, request, jsonify
from pytube import YouTube
import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_yt_as_mp3(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    filename = f"{uuid.uuid4()}.mp4"
    output_path = audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
    mp3_path = output_path.replace(".mp4", ".mp3")
    AudioSegment.from_file(output_path).export(mp3_path, format="mp3")
    os.remove(output_path)
    return mp3_path

def transcribe_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_path)
    wav_path = audio_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    os.remove(wav_path)
    return text

@app.route("/api/yt-to-text", methods=["POST"])
def yt_to_text():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        mp3_path = download_yt_as_mp3(url)
        transcript = transcribe_audio_to_text(mp3_path)
        os.remove(mp3_path)
        return jsonify({"text": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)