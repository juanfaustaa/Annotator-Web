"""Local chord annotation server.

Downloads YouTube audio to a temp folder, detects beats, and serves the
Chordify-style editor in ./static. Audio files are temporary: they are
deleted after export (DELETE /api/session/<id>) and on server start.
"""
import os
import re
import shutil
import subprocess
import uuid

import librosa
import numpy as np
import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(ROOT, "tmp")
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
SR = 44100

app = FastAPI()


def clean_tmp():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP, exist_ok=True)


def session_dir(sid):
    if not re.fullmatch(r"[0-9a-f]{32}", sid):
        raise HTTPException(400, "invalid session id")
    return os.path.join(TMP, sid)


class LoadReq(BaseModel):
    url: str


def detect_beats(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", trim=False)
    tempo = float(np.atleast_1d(tempo)[0])
    return tempo, [round(float(b), 3) for b in beats]


@app.post("/api/load")
def load(req: LoadReq):
    sid = uuid.uuid4().hex
    d = os.path.join(TMP, sid)
    os.makedirs(d)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(d, "src.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
        src = next(os.path.join(d, f) for f in os.listdir(d) if f.startswith("src."))
        wav = os.path.join(d, "audio.wav")
        # Decode once to PCM WAV so the browser and beat tracker see identical
        # sample timing (no MP3/AAC encoder-delay ambiguity).
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(SR), wav], check=True)
        os.remove(src)
        tempo, beats = detect_beats(wav)
    except Exception as e:
        shutil.rmtree(d, ignore_errors=True)
        raise HTTPException(500, "Gagal memuat audio: %s" % e)
    return {
        "id": sid,
        "videoId": info.get("id"),
        "title": info.get("title") or "untitled",
        "duration": round(librosa.get_duration(path=wav), 3),
        "tempo": round(tempo, 2),
        "beats": beats,
    }


@app.get("/api/audio/{sid}")
def audio(sid: str):
    path = os.path.join(session_dir(sid), "audio.wav")
    if not os.path.exists(path):
        raise HTTPException(404, "audio sudah dihapus")
    return FileResponse(path, media_type="audio/wav")


@app.delete("/api/session/{sid}")
def delete_session(sid: str):
    shutil.rmtree(session_dir(sid), ignore_errors=True)
    return {"deleted": sid}


app.mount("/", StaticFiles(directory=os.path.join(ROOT, "static"), html=True), name="static")

clean_tmp()
