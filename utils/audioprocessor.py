import os
import shutil
import yt_dlp
from pydub import AudioSegment

def _resolve_ffmpeg_dir() -> str:
    env_dir = os.getenv("FFMPEG_DIR")
    if env_dir and os.path.isfile(os.path.join(env_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")):
        return env_dir
    ffmpeg_on_path = shutil.which("ffmpeg")
    if ffmpeg_on_path:
        return os.path.dirname(ffmpeg_on_path)
    fallback = r"C:\Users\kartik tiwari\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin"
    if os.path.isdir(fallback):
        return fallback
    raise FileNotFoundError(
        "ffmpeg not found. Install it and either add it to PATH, or set the "
        "FFMPEG_DIR environment variable to its 'bin' folder."
    )

FFMPEG_DIR = _resolve_ffmpeg_dir()
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]
DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def _write_cookies_file():
    """Writes YOUTUBE_COOKIES secret (if present) to a temp cookies file, and returns its path."""
    cookies_content = os.getenv("YOUTUBE_COOKIES")
    if not cookies_content:
        return None
    cookies_path = os.path.join(os.getcwd(), "cookies_runtime.txt")
    with open(cookies_path, "w") as f:
        f.write(cookies_content)
    return cookies_path

_ffmpeg_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
_ffprobe_exe = "ffprobe.exe" if os.name == "nt" else "ffprobe"
AudioSegment.converter = os.path.join(FFMPEG_DIR, _ffmpeg_exe)
AudioSegment.ffmpeg = os.path.join(FFMPEG_DIR, _ffmpeg_exe)
AudioSegment.ffprobe = os.path.join(FFMPEG_DIR, _ffprobe_exe)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    cookies_path = _write_cookies_file()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "ffmpeg_location": FFMPEG_DIR,
    }

    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)
    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
