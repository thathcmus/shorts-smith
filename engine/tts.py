"""
Xử lý Text-to-Speech (Edge-TTS) và tự động tạo phụ đề (Word/Sentence Boundary).
"""
import asyncio
import os
import re
import subprocess
import edge_tts
from engine.config import FFMPEG_EXE, DEFAULT_VOICE, TEMP_DIR

def get_audio_duration(audio_path: str) -> float:
    """Đo thời lượng chính xác của tệp âm thanh qua ffprobe/ffmpeg."""
    cmd = [FFMPEG_EXE, "-i", audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        h, m_, s = m.groups()
        return int(h) * 3600 + int(m_) * 60 + float(s)
    return 5.0

async def synthesize_speech(
    text: str,
    output_audio: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "-1%",
    volume: str = "+0%"
) -> float:
    """
    Chuyển văn bản thành giọng nói MP3 qua Edge-TTS.
    Trả về thời lượng âm thanh (giây).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_audio)), exist_ok=True)
    comm = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await comm.save(output_audio)
    return get_audio_duration(output_audio)

def format_ass_timestamp(seconds: float) -> str:
    """Đổi giây sang định dạng thời gian ASS: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(
    scenes_data: list,
    output_ass: str,
    width: int = 1080,
    height: int = 1920,
    font_size: int = 56,
    font_name: str = "Segoe UI"
) -> str:
    """
    Tạo tệp phụ đề định dạng ASS với phong cách Amber Gold / Viền đen điện ảnh.
    scenes_data: list các dict {"text": str, "duration": float}
    """
    # Màu sắc ASS: &HAABBGGRR (Alpha-Blue-Green-Red)
    # &H0020E0FF = Vàng hổ phách rực rỡ (Amber Gold)
    # &H00000000 = Viền đen tuyền
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CineSub,{font_name},{font_size},&H0020E0FF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,3,2,60,60,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    current_time = 0.0

    for item in scenes_data:
        text = item["text"].strip()
        dur = item["duration"]
        start_ts = format_ass_timestamp(current_time)
        end_ts = format_ass_timestamp(current_time + dur)

        # Ngắt dòng thông minh nếu câu dài trên 8 từ để hiển thị đẹp mắt trên màn hình dọc
        words = text.split()
        if len(words) > 7:
            half = len(words) // 2
            formatted_text = " ".join(words[:half]) + "\\N" + " ".join(words[half:])
        else:
            formatted_text = text

        dialogues.append(f"Dialogue: 0,{start_ts},{end_ts},CineSub,,0,0,0,,{formatted_text}")
        current_time += dur

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")

    return output_ass
