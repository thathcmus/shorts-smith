"""
Bộ lọc chuyển động máy quay điện ảnh Ken Burns, Color Grading và xử lý video footage qua FFmpeg.
"""
import os

def get_cinematic_image_filter(
    effect: str,
    duration: float,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Sinh chuỗi filter cho ảnh tĩnh: Ken Burns zoompan + Cinematic Color Grading + Vignette tối 4 góc.
    """
    frames = int(duration * fps)

    if effect == "zoom_in_fast":
        zoom_expr = "zoompan=z='min(zoom+0.0022,1.32)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_in_slow":
        zoom_expr = "zoompan=z='min(zoom+0.0013,1.22)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_out":
        zoom_expr = "zoompan=z='if(eq(on,1),1.30,max(1.0,zoom-0.0020))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "pan_down":
        zoom_expr = "zoompan=z=1.24:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom, on*0.75)'"
    elif effect == "pan_up":
        zoom_expr = "zoompan=z=1.24:x='iw/2-(iw/zoom/2)':y='max(0, (ih-ih/zoom) - on*0.75)'"
    elif effect == "pan_right":
        zoom_expr = "zoompan=z=1.24:x='min(iw-iw/zoom, on*0.75)':y='ih/2-(ih/zoom/2)'"
    else:
        zoom_expr = "zoompan=z='min(zoom+0.0016,1.26)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

    # Chuỗi filter: Zoompan -> Scale -> Color Grading (Contrast + Saturation) -> Vignette điện ảnh
    vf = (
        f"{zoom_expr}:d={frames}:s={width}x{height}:fps={fps},"
        f"eq=contrast=1.10:brightness=-0.02:saturation=1.18,"
        f"vignette=PI/4.5"
    )
    return vf

def get_cinematic_video_filter(
    duration: float,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Sinh chuỗi filter cho video footage thực tế:
    Scale & crop 9:16 + Color Grading + Vignette tối 4 góc.
    """
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"fps={fps},"
        f"eq=contrast=1.08:brightness=-0.01:saturation=1.15,"
        f"vignette=PI/5"
    )

def is_video_file(path: str) -> bool:
    """Kiểm tra tệp đầu vào là video hay hình ảnh."""
    ext = os.path.splitext(path)[1].lower()
    return ext in [".mp4", ".mov", ".mkv", ".webm", ".avi"]
