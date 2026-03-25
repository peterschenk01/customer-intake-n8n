from fastapi import APIRouter, HTTPException, Request, UploadFile, File
import tempfile
from faster_whisper import WhisperModel
import os
import requests
import time

BASE_URL = "https://api.assemblyai.com"
ASSEMBLY_AI_KEY=os.getenv("ASSEMBLY_AI_KEY")

DEVICE = "cpu"
model = WhisperModel("small", device=DEVICE, compute_type="int8")

router = APIRouter(prefix="/api")


@router.get("/")
async def home(request: Request):
    return {"status": "api"}


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1] or ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(tmp_path)
    except Exception as e:
        os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)

    return {
        "segments": [segment.text for segment in segments],
        "language": info.language
    }


@router.post("/diarize")
async def diarize(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[-1] or ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)
        tmp_path = tmp.name

    headers = {
        "authorization": ASSEMBLY_AI_KEY
    }

    with open(tmp_path, "rb") as f:
        response = requests.post(BASE_URL + "/v2/upload",
                                headers=headers,
                                data=f)
    
    audio_url = response.json()["upload_url"]

    data = {
        "audio_url": audio_url,
        "language_detection": True,
        "speaker_labels": True,
        "speech_models": ["universal-3-pro", "universal-2"],
        "speakers_expected": 2,
    }

    url = BASE_URL + "/v2/transcript"
    response = requests.post(url, json=data, headers=headers)

    transcript_id = response.json()['id']
    polling_endpoint = BASE_URL + "/v2/transcript/" + transcript_id

    while True:
        transcription_result = requests.get(polling_endpoint, headers=headers).json()
        transcript_text = transcription_result['text']

        if transcription_result['status'] == 'completed':
            break

        elif transcription_result['status'] == 'error':
            raise HTTPException(f"Transcription failed: {transcription_result['error']}")

        else:
            time.sleep(3)

    words = transcription_result['words']

    segments = []
    current = None

    for w in words:
        if current is None:
            current = {
                "speaker": w["speaker"],
                "start": w["start"],
                "end": w["end"],
                "text": w["text"]
            }
        elif w["speaker"] == current["speaker"]:
            current["end"] = w["end"]
            current["text"] += " " + w["text"]
        else:
            segments.append(current)
            current = {
                "speaker": w["speaker"],
                "start": w["start"],
                "end": w["end"],
                "text": w["text"]
            }

    if current is not None:
        segments.append(current)

    return {
        "transcript_text": transcript_text,
        "segments": segments
    }
