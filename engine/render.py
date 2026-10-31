"""
Bộ dựng video (Video Renderer), ghép nối clips, hòa âm BGM và nung phụ đề qua FFmpeg.
"""
import os
import subprocess
import wave
import numpy as np
from engine.config import FFMPEG_EXE, DEFAULT_FPS, DEFAULT_VIDEO_CODEC, DEFAULT_AUDIO_BITRATE
from engine.effects import get_ken_burns_filter

def create_tension_bgm(duration: float, output_wav: str) -> str:
    """
    Tự động tổng hợp nhạc nền Tension/Cinematic Suspense:
    Sub-bass 55Hz rền vang + Tiếng tim đập dồn dập (Heartbeat) + Sóng bí ẩn 432Hz.
    Không phụ thuộc vào file nhạc ngoài, sinh tức thì theo thời lượng chính xác.
    """
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # 1. Âm trầm Sub-bass rung rợn (55Hz + 110Hz)
    sub = 0.42 * np.sin(2 * np.pi * 55 * t) + 0.22 * np.sin(2 * np.pi * 110 * t)
    swell = 0.65 + 0.35 * np.sin(2 * np.pi * 0.15 * t)

    # 2. Tiếng nhịp tim hồi hộp (Heartbeat 'thump-thump') mỗi 1.4s
    hb = np.zeros_like(t)
    period = int(sr * 1.4)
    for i in range(0, len(t), period):
        end1 = min(i + int(sr * 0.12), len(t))
        length1 = end1 - i
        hb[i:end1] += np.sin(2 * np.pi * 48 * np.linspace(0, 0.12, length1)) * np.exp(-np.linspace(0, 6, length1))

        start2 = i + int(sr * 0.22)
        end2 = min(start2 + int(sr * 0.10), len(t))
        if start2 < len(t):
            length2 = end2 - start2
            hb[start2:end2] += 0.7 * np.sin(2 * np.pi * 44 * np.linspace(0, 0.10, length2)) * np.exp(-np.linspace(0, 6, length2))

    # 3. Âm thanh tần số vũ trụ bí ẩn (432Hz)
    mystery = 0.08 * np.sin(2 * np.pi * 432 * t + 0.2 * np.sin(2 * np.pi * 0.4 * t))

    combined = (sub * swell + hb * 0.75 + mystery) * 0.45
    audio = np.int16(combined / (np.max(np.abs(combined)) + 1e-6) * 32767)

    with wave.open(output_wav, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio.tobytes())

    return output_wav

def render_scene_clip(
    image_path: str,
    audio_path: str,
    output_clip_path: str,
    duration: float,
    effect: str = "zoom_in_slow",
    width: int = 1080,
    height: int = 1920,
    fps: int = DEFAULT_FPS
) -> str:
    """
    Render một cảnh gồm [Ảnh tĩnh + Giọng đọc] thành một đoạn clip MP4 có hiệu ứng máy quay.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)
    vf = get_ken_burns_filter(effect, duration, fps=fps, width=width, height=height)

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", DEFAULT_VIDEO_CODEC,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", DEFAULT_AUDIO_BITRATE,
        "-shortest",
        output_clip_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_clip_path

def assemble_final_video(
    clip_paths: list,
    output_video_path: str,
    bgm_path: str = None,
    subtitles_path: str = None,
    bgm_volume: float = 0.22,
    temp_dir: str = None
) -> str:
    """
    Ghép nối các clips, hòa âm Voice + BGM và nung phụ đề ASS thành video cuối cùng.
    """
    if temp_dir is None:
        temp_dir = os.path.dirname(os.path.abspath(output_video_path))
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Tạo file concat list
    concat_list_file = os.path.join(temp_dir, "concat_manifest.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for clip in clip_paths:
            # Đường dẫn chuẩn hóa cho FFmpeg concat
            safe_path = os.path.abspath(clip).replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    # 2. Ghép nối các clip video thô
    raw_merged_path = os.path.join(temp_dir, "raw_merged.mp4")
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-c", "copy",
        raw_merged_path
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Hòa âm + Phụ đề
    safe_sub_path = os.path.abspath(subtitles_path).replace("\\", "/").replace(":", "\\:") if subtitles_path else None
    
    # Xây dựng lệnh filter phức hợp
    if bgm_path and os.path.exists(bgm_path) and safe_sub_path and os.path.exists(subtitles_path):
        final_cmd = [
            FFMPEG_EXE, "-y",
            "-i", raw_merged_path,
            "-i", bgm_path,
            "-filter_complex",
            f"[0:v]subtitles='{safe_sub_path}'[vsub];"
            f"[0:a]volume=1.0[v_voice];"
            f"[1:a]volume={bgm_volume}[v_bgm];"
            f"[v_voice][v_bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[vsub]",
            "-map", "[aout]",
            "-c:v", DEFAULT_VIDEO_CODEC,
            "-c:a", "aac",
            "-b:a", DEFAULT_AUDIO_BITRATE,
            "-pix_fmt", "yuv420p",
            output_video_path
        ]
    elif safe_sub_path and os.path.exists(subtitles_path):
        final_cmd = [
            FFMPEG_EXE, "-y",
            "-i", raw_merged_path,
            "-vf", f"subtitles='{safe_sub_path}'",
            "-c:v", DEFAULT_VIDEO_CODEC,
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            output_video_path
        ]
    else:
        final_cmd = [
            FFMPEG_EXE, "-y",
            "-i", raw_merged_path,
            "-c", "copy",
            output_video_path
        ]

    subprocess.run(final_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_video_path
