"""
Cấu hình mặc định cho AI Video Producer Engine.
"""
import os
import sys
import imageio_ffmpeg

# Đường dẫn FFmpeg
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Độ phân giải mặc định
RESOLUTIONS = {
    "vertical": (1080, 1920),    # 9:16 (Shorts, TikTok, Reels)
    "horizontal": (1920, 1080),  # 16:9 (YouTube standard)
}

DEFAULT_ASPECT = "vertical"
DEFAULT_FPS = 30
DEFAULT_AUDIO_BITRATE = "192k"
DEFAULT_VIDEO_CODEC = "libx264"

# Cấu hình giọng đọc Edge-TTS
VOICES = {
    "vi_nam": "vi-VN-NamMinhNeural",     # Nam đanh thép, bí ẩn, tài liệu
    "vi_nu": "vi-VN-HoaiMyNeural",       # Nữ truyền cảm, ấm áp
    "en_male": "en-US-ChristopherNeural",# Nam tiếng Anh trầm
    "en_female": "en-US-JennyNeural",   # Nữ tiếng Anh tự nhiên
}
DEFAULT_VOICE = VOICES["vi_nam"]
DEFAULT_SPEECH_RATE = "+50%"  # Tốc độ đọc 1.5x chuẩn TikTok dồn dập, giữ chân người xem
DEFAULT_PITCH = "+0Hz"


# Thư mục lưu trữ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp_build")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
