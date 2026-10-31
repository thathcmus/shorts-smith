"""
Bộ lọc chuyển động máy quay điện ảnh Ken Burns và hiệu ứng hình ảnh qua FFmpeg.
"""

def get_ken_burns_filter(
    effect: str,
    duration: float,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Sinh chuỗi filter `zoompan` và scale tương ứng cho FFmpeg.
    Đảm bảo chuyển động mượt mà, không bị rung giật viền.
    """
    frames = int(duration * fps)

    if effect == "zoom_in_fast":
        zoom_expr = "zoompan=z='min(zoom+0.0022,1.30)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_in_slow":
        zoom_expr = "zoompan=z='min(zoom+0.0012,1.20)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_out":
        zoom_expr = "zoompan=z='if(eq(on,1),1.28,max(1.0,zoom-0.0018))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "pan_down":
        zoom_expr = "zoompan=z=1.22:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom, on*0.60)'"
    elif effect == "pan_up":
        zoom_expr = "zoompan=z=1.22:x='iw/2-(iw/zoom/2)':y='max(0, (ih-ih/zoom) - on*0.60)'"
    elif effect == "pan_right":
        zoom_expr = "zoompan=z=1.22:x='min(iw-iw/zoom, on*0.60)':y='ih/2-(ih/zoom/2)'"
    else:
        # Mặc định: zoom in êm dịu
        zoom_expr = "zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

    # Kết hợp filter scale và fps
    return f"{zoom_expr}:d={frames}:s={width}x{height}:fps={fps}"

def get_smart_blur_background_filter(
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Tạo filter làm mờ hậu cảnh (Blur Letterbox) khi hình ảnh không đúng tỉ lệ khung hình.
    Layer dưới: Phóng to toàn màn hình + Boxblur làm mờ.
    Layer trên: Giữ nguyên tỉ lệ ảnh gốc, căn giữa sắc nét.
    """
    return (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},boxblur=20:10[bg];"
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
