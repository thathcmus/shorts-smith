"""
Bộ dựng video (Video Renderer) nâng cấp: hỗ trợ cả Video Footage thật, BGM MP3 điện ảnh và phụ đề TikTok.
"""
import glob
import os
import random
import subprocess
from engine.config import (
    FFMPEG_EXE,
    DEFAULT_FPS,
    DEFAULT_VIDEO_CODEC,
    DEFAULT_AUDIO_BITRATE,
    BASE_DIR,
)
from engine.effects import (
    get_cinematic_image_filter,
    get_cinematic_video_filter,
    is_video_file,
)

def get_best_bgm_track(custom_path: str = None) -> str:
    """
    Lấy bản nhạc nền điện ảnh MP3 chất lượng cao nhất:
    Ưu tiên tệp chỉ định -> thư mục assets/audio/*.mp3 -> tạo fallback.
    """
    if custom_path and os.path.exists(custom_path):
        return custom_path

    audio_dir = os.path.join(BASE_DIR, "assets", "audio")
    tracks = glob.glob(os.path.join(audio_dir, "*.mp3"))
    if tracks:
        # Chọn ngẫu nhiên hoặc bài đầu tiên
        return tracks[0]

    return None

def render_scene_clip(
    media_path: str,
    audio_path: str,
    output_clip_path: str,
    duration: float,
    effect: str = "zoom_in_slow",
    width: int = 1080,
    height: int = 1920,
    fps: int = DEFAULT_FPS
) -> str:
    """
    Render một cảnh: Nhận đầu vào là [Hình ảnh] HOẶC [Video clip ngắn] kết hợp với [Giọng đọc].
    Áp dụng bộ lọc điện ảnh, vignette và xuất ra clip MP4.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

    if not os.path.exists(media_path):
        raise FileNotFoundError(f"Không tìm thấy file hình ảnh/video tài nguyên: '{media_path}'")

    if is_video_file(media_path):
        # Nguồn là Video footage chuyển động thật
        vf = get_cinematic_video_filter(duration, fps=fps, width=width, height=height)
        cmd = [
            FFMPEG_EXE, "-y",
            "-stream_loop", "-1",  # Lặp lại nếu clip ngắn hơn câu thoại
            "-i", media_path,
            "-i", audio_path,
            "-vf", vf,
            "-t", str(duration),
            "-c:v", DEFAULT_VIDEO_CODEC,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", DEFAULT_AUDIO_BITRATE,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_clip_path
        ]
    else:
        # Nguồn là Hình ảnh tĩnh -> Áp dụng Ken Burns + Color Grade + Vignette
        vf = get_cinematic_image_filter(effect, duration, fps=fps, width=width, height=height)
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", media_path,
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

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else f"Mã lỗi {e.returncode}"
        raise RuntimeError(f"FFmpeg render thất bại khi xử lý '{media_path}':\n{err_msg}")
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
    Ghép nối các clips, hòa âm Voiceover + BGM MP3 điện ảnh và nung phụ đề ASS.
    """
    if temp_dir is None:
        temp_dir = os.path.dirname(os.path.abspath(output_video_path))
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Tạo manifest ghép video
    concat_list_file = os.path.join(temp_dir, "concat_manifest.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for clip in clip_paths:
            safe_path = os.path.abspath(clip).replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    # 2. Concat các clip video
    raw_merged_path = os.path.join(temp_dir, "raw_merged.mp4")
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-c", "copy",
        raw_merged_path
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Chuẩn hóa đường dẫn phụ đề cho FFmpeg filter
    safe_sub_path = os.path.abspath(subtitles_path).replace("\\", "/").replace(":", "\\:") if subtitles_path else None

    # 4. Hòa âm nhạc nền BGM thật và nung phụ đề
    if bgm_path and os.path.exists(bgm_path) and safe_sub_path and os.path.exists(subtitles_path):
        final_cmd = [
            FFMPEG_EXE, "-y",
            "-i", raw_merged_path,
            "-stream_loop", "-1", "-i", bgm_path,
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
