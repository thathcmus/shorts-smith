"""
Xử lý Text-to-Speech (Edge-TTS) và tự động tạo phụ đề phong cách TikTok Dynamic/Karaoke.
"""
import asyncio
import os
import re
import subprocess
import edge_tts
from engine.config import FFMPEG_EXE, VOICES, DEFAULT_VOICE, DEFAULT_SPEECH_RATE, TEMP_DIR

def get_audio_duration(audio_path: str) -> float:
    """Đo thời lượng chính xác của tệp âm thanh qua ffmpeg."""
    cmd = [FFMPEG_EXE, "-i", audio_path]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        h, m_, s = m.groups()
        return int(h) * 3600 + int(m_) * 60 + float(s)
    return 5.0

async def synthesize_speech_with_words(
    text: str,
    output_audio: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_SPEECH_RATE,
    volume: str = "+0%",
    pitch: str = "+0Hz",
    max_retries: int = 5
) -> tuple[float, list]:
    """
    Chuyển văn bản thành giọng nói MP3 qua Edge-TTS và ghi nhận timestamp của từng từ (WordBoundary).
    Có cơ chế tự động thử lại (retry) thông minh đa tầng:
    - Lần 0: Giọng chính kèm WordBoundary
    - Lần 1: Giọng chính tiêu chuẩn (tự động nội suy nhịp từ)
    - Lần 2: Giọng luân phiên (Fallback Voice) kèm WordBoundary
    - Lần 3+: Giọng luân phiên tiêu chuẩn kèm nội suy nhịp từ
    Trả về: (thời lượng_giây, danh_sách_từ_kèm_timestamp)
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_audio)), exist_ok=True)
    
    # Làm sạch ký tự đặc biệt, dấu gạch nối và ngoặc kép lạ tránh kẹt parser TTS
    clean_text = (
        text.replace("...", ". ")
        .replace("..", ". ")
        .replace("–", "-")
        .replace("—", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .strip()
    )
    
    alt_voice = VOICES.get("vi_nu", "vi-VN-HoaiMyNeural") if voice == VOICES.get("vi_nam", "vi-VN-NamMinhNeural") else VOICES.get("vi_nam", "vi-VN-NamMinhNeural")
    last_err = None

    for attempt in range(max_retries):
        cur_voice = voice if attempt < 2 else alt_voice
        use_wb = (attempt in (0, 2))
        
        try:
            if os.path.exists(output_audio):
                try:
                    os.remove(output_audio)
                except OSError:
                    pass

            kwargs = {
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
            }
            if use_wb:
                kwargs["boundary"] = "WordBoundary"

            comm = edge_tts.Communicate(clean_text, cur_voice, **kwargs)

            words = []
            with open(output_audio, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        words.append({
                            "word": chunk["text"],
                            "start": chunk["offset"] / 10000000.0,
                            "end": (chunk["offset"] + chunk["duration"]) / 10000000.0
                        })
            
            if os.path.exists(output_audio) and os.path.getsize(output_audio) > 1024:
                dur = get_audio_duration(output_audio)
                # Nếu không bắt được nhịp từ trực tiếp, tự động nội suy đều theo thời lượng để Karaoke vẫn nhảy đẹp
                if not words:
                    all_tokens = clean_text.split()
                    if all_tokens:
                        step = dur / len(all_tokens)
                        words = [{
                            "word": tok,
                            "start": round(i * step, 2),
                            "end": round((i + 1) * step, 2)
                        } for i, tok in enumerate(all_tokens)]
                return dur, words
            else:
                raise RuntimeError(f"Audio file empty or corrupted (<1KB): {output_audio}")
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                backoff = 1.8 * (attempt + 1)
                await asyncio.sleep(backoff)
            else:
                raise last_err

def format_ass_timestamp(seconds: float) -> str:
    """Đổi giây sang định dạng thời gian ASS: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

def generate_tiktok_style_subtitles(
    scenes_data: list,
    output_ass: str,
    width: int = 1080,
    height: int = 1920,
    font_size: int = 70,
    font_name: str = "Segoe UI Black"
) -> str:
    """
    Tạo phụ đề phong cách TikTok/CapCut Viral:
    - Hiển thị theo cụm từ ngắn (2 - 4 từ mỗi lượt) ở 1/3 dưới màn hình (MarginV=420).
    - Cỡ chữ lớn, viền đen dày, đổ bóng sâu.
    - Màu chữ: Vàng Neon (&H0000E5FF&) kết hợp Trắng tinh khiết (&H00FFFFFF&).
    """
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTokActive,{font_name},{font_size},&H0000E5FF,&H000000FF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,6,3,2,60,60,450,1
Style: TikTokNormal,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,6,3,2,60,60,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    global_time = 0.0

    for scene in scenes_data:
        scene_words = scene.get("words", [])
        scene_dur = scene["duration"]
        
        if scene_words:
            # Nhóm các từ thành cụm ngắn từ 2 đến 4 từ để hiển thị nhịp nhàng
            chunks = []
            current_chunk = []
            
            for w in scene_words:
                current_chunk.append(w)
                # Tách nhóm khi có dấu câu hoặc đủ 3-4 từ
                if len(current_chunk) >= 3 or w["word"].endswith((".", ",", "!", "?", "...", ":")):
                    chunks.append(current_chunk)
                    current_chunk = []
            if current_chunk:
                chunks.append(current_chunk)

            for chunk in chunks:
                chunk_start = global_time + chunk[0]["start"]
                chunk_end = global_time + chunk[-1]["end"]
                
                # Tạo hiệu ứng đổi màu từng từ trong cụm (Karaoke Pop-up)
                for active_idx, target_word in enumerate(chunk):
                    w_start = global_time + target_word["start"]
                    w_end = global_time + target_word["end"]
                    
                    # Ghép các từ: từ đang đọc có màu vàng sáng, các từ khác màu trắng
                    rendered_words = []
                    for idx, item in enumerate(chunk):
                        if idx == active_idx:
                            rendered_words.append(f"{{\\c&H0000E5FF\\b1}}{item['word']}{{\\r}}")
                        else:
                            rendered_words.append(f"{{\\c&H00FFFFFF\\b1}}{item['word']}{{\\r}}")
                            
                    line_text = " ".join(rendered_words)
                    start_ts = format_ass_timestamp(w_start)
                    end_ts = format_ass_timestamp(w_end)
                    dialogues.append(f"Dialogue: 0,{start_ts},{end_ts},TikTokActive,,0,0,0,,{line_text}")
        else:
            # Fallback nếu không có word timing
            text = scene["text"]
            start_ts = format_ass_timestamp(global_time)
            end_ts = format_ass_timestamp(global_time + scene_dur)
            dialogues.append(f"Dialogue: 0,{start_ts},{end_ts},TikTokActive,,0,0,0,,{text}")

        global_time += scene_dur

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")

    return output_ass
