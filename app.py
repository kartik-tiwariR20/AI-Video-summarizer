"""
AI Video Assistant — Streamlit UI
Wraps the existing pipeline in main.py (run_pipeline) with a polished,
animated, interactive front-end.
"""

import time
import streamlit as st

from main import run_pipeline
from core.rag import ask_question

# ──────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — gradients, glassmorphism cards, animations
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

/* ---------- Animated gradient background ---------- */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ---------- Fade / slide-in animation for content blocks ---------- */
@keyframes fadeSlideUp {
    0%   { opacity: 0; transform: translateY(18px); }
    100% { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeSlideUp 0.6s ease-out both;
}

/* ---------- Hero title ---------- */
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #7f5af0, #2cb67d, #7f5af0);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 6s linear infinite;
    margin-bottom: 0;
}
@keyframes shine {
    to { background-position: 200% center; }
}
.hero-subtitle {
    text-align: center;
    color: #b8b8d1;
    font-size: 1.05rem;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
    letter-spacing: 0.3px;
}

/* ---------- Glass cards ---------- */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    margin-bottom: 1.2rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(127, 90, 240, 0.25);
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #f4f4f8;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-body {
    color: #d4d4e4;
    font-size: 0.98rem;
    line-height: 1.65;
    white-space: pre-wrap;
}

/* ---------- Buttons ---------- */
.stButton > button {
    background: linear-gradient(90deg, #7f5af0, #2cb67d);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.6rem;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.3px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 18px rgba(127, 90, 240, 0.35);
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 28px rgba(127, 90, 240, 0.5);
    color: white;
}

/* ---------- Inputs ---------- */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: rgba(255,255,255,0.07) !important;
    color: #f4f4f8 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.85);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px 10px 0 0;
    padding: 10px 18px;
    color: #b8b8d1;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(127, 90, 240, 0.25) !important;
    color: #ffffff !important;
}

/* ---------- Chat bubbles ---------- */
.stChatMessage {
    animation: fadeSlideUp 0.4s ease-out both;
}

/* ---------- Badge / pill ---------- */
.pill {
    display: inline-block;
    background: rgba(44, 182, 125, 0.18);
    color: #2cb67d;
    border: 1px solid rgba(44, 182, 125, 0.4);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-left: 8px;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# ──────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title fade-in">🎬 AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle fade-in">Turn any video or recording into a transcript, '
    'summary, action items — and a chat partner that knows the whole conversation.</div>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — INPUT CONTROLS
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Setup")
    st.markdown("Provide a YouTube URL or upload a local audio/video file.")

    input_mode = st.radio("Input type", ["YouTube URL", "Upload a file"], horizontal=False)

    source = None
    uploaded_file = None

    if input_mode == "YouTube URL":
        source = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    else:
        uploaded_file = st.file_uploader(
            "Upload audio/video", type=["mp3", "wav", "m4a", "mp4", "mov", "mkv"]
        )
        if uploaded_file is not None:
            import os
            os.makedirs("uploads", exist_ok=True)
            local_path = os.path.join("uploads", uploaded_file.name)
            with open(local_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            source = local_path
            st.success(f"Saved: {uploaded_file.name}")

    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    st.markdown("---")
    run_clicked = st.button("🚀 Run Analysis", use_container_width=True)
    st.markdown("---")
    st.caption("Built with Streamlit · Whisper · LangChain")

# ──────────────────────────────────────────────────────────────────────────
# RUN PIPELINE
# ──────────────────────────────────────────────────────────────────────────
if run_clicked:
    if not source:
        st.warning("Please provide a YouTube URL or upload a file first.")
    else:
        st.session_state.processing = True
        st.session_state.chat_history = []

        progress_container = st.empty()
        steps = [
            "Downloading / preparing audio...",
            "Chunking audio...",
            "Transcribing with Whisper...",
            "Generating title & summary...",
            "Extracting action items & decisions...",
            "Building chat index...",
        ]
        with progress_container.container():
            st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
            bar = st.progress(0, text=steps[0])
            for i, step_text in enumerate(steps[:-1]):
                bar.progress(int((i / len(steps)) * 100), text=step_text)
                time.sleep(0.35)  # cosmetic pacing only
            st.markdown('</div>', unsafe_allow_html=True)

            try:
                result = run_pipeline(source, language)
                bar.progress(100, text="Done!")
                st.session_state.result = result
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.session_state.result = None
                st.error(f"Something went wrong while processing: {e}")

        st.session_state.processing = False
        progress_container.empty()

# ──────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ──────────────────────────────────────────────────────────────────────────
result = st.session_state.result

if result:
    st.markdown(
        f'<div class="glass-card fade-in">'
        f'<div class="section-title">📌 {result["title"]} <span class="pill">Ready</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["📋 Summary", "✅ Action Items", "🔑 Decisions", "❓ Questions", "📝 Transcript", "💬 Chat"])

    with tabs[0]:
        st.markdown(
            f'<div class="glass-card fade-in"><div class="section-body">{result["summary"]}</div></div>',
            unsafe_allow_html=True,
        )

    with tabs[1]:
        st.markdown(
            f'<div class="glass-card fade-in"><div class="section-body">{result["action_items"]}</div></div>',
            unsafe_allow_html=True,
        )

    with tabs[2]:
        st.markdown(
            f'<div class="glass-card fade-in"><div class="section-body">{result["key_decisions"]}</div></div>',
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown(
            f'<div class="glass-card fade-in"><div class="section-body">{result["open_questions"]}</div></div>',
            unsafe_allow_html=True,
        )

    with tabs[4]:
        with st.expander("Show full transcript", expanded=False):
            st.markdown(
                f'<div class="section-body">{result["transcript"]}</div>',
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.markdown('<div class="glass-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💬 Chat with your meeting</div>', unsafe_allow_html=True)

        # render existing history
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

        question = st.chat_input("Ask something about this video...")
        if question:
            st.session_state.chat_history.append(("user", question))
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = ask_question(result["rag_chain"], question)
                    except Exception as e:
                        answer = f"⚠️ Couldn't answer that: {e}"
                st.markdown(answer)
            st.session_state.chat_history.append(("assistant", answer))

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(
        '<div class="glass-card fade-in" style="text-align:center; padding:3rem 2rem;">'
        '<div style="font-size:2.4rem;">🎥✨</div>'
        '<div class="section-title" style="justify-content:center;">Nothing analyzed yet</div>'
        '<div class="section-body" style="text-align:center;">'
        'Paste a YouTube link or upload a file in the sidebar, then hit '
        '<b>Run Analysis</b> to get started.</div></div>',
        unsafe_allow_html=True,
    )