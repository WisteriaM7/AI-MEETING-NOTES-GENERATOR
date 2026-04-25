from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import requests
import tempfile
import os

app = FastAPI(title="AI Meeting Notes Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/wave"}
OLLAMA_URL = "http://localhost:11434/api/generate"

# Load Whisper model once at startup — use "small" for better accuracy
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded.")


def call_ollama(prompt: str, timeout: int = 120) -> str:
    """Send a prompt to the local Ollama LLaMA 2 instance."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Ollama. Make sure it is running on port 11434."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


@app.get("/")
def root():
    return {"message": "AI Meeting Notes Generator API is running!"}


@app.post("/process/")
async def process_audio(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Please upload MP3 or WAV."
        )

    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Determine file extension from content type
    ext = ".wav" if "wav" in file.content_type else ".mp3"

    # Write to a temp file for Whisper
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # Step 1: Transcribe with Whisper
        result = model.transcribe(tmp_path)
        transcript = result.get("text", "").strip()
        detected_language = result.get("language", "unknown")

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail="Whisper could not extract speech from the audio. Try a clearer recording."
            )

        # Step 2: Generate meeting summary
        summary_prompt = (
            "You are an expert meeting assistant. "
            "Write a clear and concise summary (3–5 sentences) of the following meeting transcript. "
            "Focus on the main topics discussed and decisions made.\n\n"
            f"Transcript:\n{transcript}"
        )
        summary = call_ollama(summary_prompt)

        # Step 3: Extract action items
        tasks_prompt = (
            "You are an expert meeting assistant. "
            "Extract all key action items from the following meeting transcript. "
            "Format them as a numbered list. Each item should include WHO is responsible (if mentioned) and WHAT they need to do.\n\n"
            f"Transcript:\n{transcript}"
        )
        action_items = call_ollama(tasks_prompt)

        return {
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "detected_language": detected_language,
            "word_count": len(transcript.split())
        }

    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
