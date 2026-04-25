# 🎙️ AI Meeting Notes Generator (Whisper + LLaMA 2)

An AI-powered meeting assistant that transcribes audio recordings and generates structured meeting notes — all running **100% locally**, with no API keys or internet required.

---

## 🧠 Tech Stack

| Layer          | Technology                   |
|----------------|------------------------------|
| Transcription  | OpenAI Whisper (local)       |
| Summarization  | LLaMA 2 via Ollama           |
| Backend        | FastAPI + Uvicorn            |
| Frontend       | Streamlit                    |
| Audio Handling | pydub + FFmpeg               |
| Language       | Python 3.10+                 |

---

## 📁 Project Structure

```
meeting-notes-ai/
│
├── backend/
│   ├── __init__.py
│   └── main.py          # FastAPI: Whisper transcription + LLaMA summarization
│
├── frontend/
│   └── app.py           # Streamlit UI with audio player + download button
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/meeting-notes-ai.git
cd meeting-notes-ai
```

### 2. Install FFmpeg (required by Whisper)

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows — download from https://ffmpeg.org/download.html and add to PATH
```

### 3. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Ollama & Pull LLaMA 2

- Download Ollama: https://ollama.com
- Pull the model:

```bash
ollama pull llama2
```

---

## 🚀 Running the App

Open **two separate terminals**:

**Terminal 1 — Start the Backend:**

```bash
uvicorn backend.main:app --reload
```

Backend runs at: `http://localhost:8000`  
> ⚠️ Whisper loads on first startup — this may take 10–30 seconds.

**Terminal 2 — Start the Frontend:**

```bash
streamlit run frontend/app.py
```

Frontend runs at: `http://localhost:8501`

---

## 📌 API Endpoints

| Method | Endpoint     | Description                                    |
|--------|--------------|------------------------------------------------|
| GET    | `/`          | Health check                                   |
| POST   | `/process/`  | Upload audio → transcript + summary + actions  |

### Example Response

```json
{
  "transcript": "Alright everyone, let's get started...",
  "summary": "The team discussed Q3 deadlines and agreed to...",
  "action_items": "1. Ruchi to complete the API integration by Friday...",
  "detected_language": "en",
  "word_count": 342
}
```

---

## ✅ Features

- 🎤 Local Whisper transcription — no OpenAI API needed
- 🧠 LLaMA 2 summarization and action-item extraction
- 📥 Download transcript as `.txt` file directly from the UI
- 🌐 Detected language shown in the output metadata
- 📊 Word count displayed for quick reference
- Temp files cleaned up after each request
- CORS-enabled FastAPI backend with full error handling

---

## ⚡ Whisper Model Options

Edit `backend/main.py` to swap the model size:

| Model  | Speed  | Accuracy | VRAM  |
|--------|--------|----------|-------|
| `tiny` | Fastest | Lower   | ~1 GB |
| `base` | Fast    | Good    | ~1 GB |
| `small`| Medium  | Better  | ~2 GB |
| `medium`| Slow   | High    | ~5 GB |

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `ffmpeg not found` | Install FFmpeg and add it to your system PATH |
| Whisper loads slowly | Normal on first run — model downloads once |
| Ollama not connecting | Run `ollama serve` in a separate terminal |
| Timeout on long audio | Try a shorter clip first; increase timeout in `frontend/app.py` |
| Empty transcript | Ensure the recording has clear speech and minimal background noise |
