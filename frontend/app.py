import streamlit as st
import requests

st.set_page_config(
    page_title="AI Meeting Notes Generator",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ AI Meeting Notes Generator")
st.markdown("Powered by **Whisper** (transcription) + **LLaMA 2 via Ollama** (summarization) · FastAPI · Streamlit")
st.divider()

# Sidebar info
with st.sidebar:
    st.header("ℹ️ How It Works")
    st.markdown("""
1. Upload your meeting audio (MP3 or WAV)
2. Click **Generate Notes**
3. Whisper transcribes the audio locally
4. LLaMA 2 generates a summary and action items

**Models used:**
- 🎤 `Whisper base` — transcription
- 🧠 `LLaMA 2` via Ollama — summarization

**Tip:** Use the `small` Whisper model in `backend/main.py` for better accuracy on noisy recordings.
    """)
    st.divider()
    st.caption("All processing is local — no data leaves your machine.")

# File upload
audio_file = st.file_uploader(
    "Upload your meeting audio:",
    type=["mp3", "wav"],
    help="Supported formats: MP3, WAV"
)

if audio_file is not None:
    st.audio(audio_file, format=audio_file.type)

    file_size_kb = len(audio_file.getvalue()) / 1024
    st.caption(f"📁 {audio_file.name} · {file_size_kb:.1f} KB")

    st.divider()

    if st.button("🚀 Generate Notes", type="primary", use_container_width=True):
        with st.spinner("Step 1/3 — Transcribing audio with Whisper (this may take a minute)..."):
            try:
                audio_file.seek(0)
                files = {
                    "file": (
                        audio_file.name,
                        audio_file.getvalue(),
                        audio_file.type
                    )
                }

                # Use a long timeout — Whisper + 2x LLaMA calls can take a while
                response = requests.post(
                    "http://localhost:8000/process/",
                    files=files,
                    timeout=300
                )

                if response.status_code == 200:
                    output = response.json()

                    # Metadata row
                    meta_col1, meta_col2, meta_col3 = st.columns(3)
                    with meta_col1:
                        st.metric("📝 Word Count", output.get("word_count", "—"))
                    with meta_col2:
                        st.metric("🌐 Detected Language", output.get("detected_language", "—").upper())
                    with meta_col3:
                        st.metric("✅ Status", "Complete")

                    st.divider()

                    # Summary
                    st.subheader("📝 Meeting Summary")
                    st.info(output.get("summary", "No summary generated."))

                    # Action items
                    st.subheader("✅ Action Items")
                    st.success(output.get("action_items", "No action items found."))

                    # Full transcript in expander
                    with st.expander("📄 Full Transcript", expanded=False):
                        transcript_text = output.get("transcript", "")
                        st.text_area(
                            "Transcript:",
                            value=transcript_text,
                            height=300,
                            label_visibility="collapsed"
                        )
                        st.download_button(
                            label="⬇️ Download Transcript (.txt)",
                            data=transcript_text,
                            file_name=f"{audio_file.name.rsplit('.', 1)[0]}_transcript.txt",
                            mime="text/plain"
                        )

                elif response.status_code == 400:
                    st.error(f"❌ {response.json().get('detail', 'Bad request.')}")
                elif response.status_code == 422:
                    st.error(f"❌ {response.json().get('detail', 'Could not process audio.')}")
                elif response.status_code == 503:
                    st.error("❌ Ollama is not running. Start it with `ollama serve`.")
                else:
                    st.error(f"❌ Server error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the backend. Run: `uvicorn backend.main:app --reload`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Large audio files take longer — try a shorter clip first.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
else:
    st.info("👆 Upload an MP3 or WAV file to get started.")

st.divider()
st.caption(
    "Ensure Ollama is running (`ollama serve`), LLaMA 2 is pulled (`ollama pull llama2`), "
    "and the backend is active (`uvicorn backend.main:app --reload`)."
)
