import asyncio
import os
import re
import sys
import subprocess
import wave
import numpy as np
import edge_tts
import imageio_ffmpeg

# Đảm bảo console Windows in tiếng Việt UTF-8 mượt mà
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# ==========================================
# CẤU HÌNH KỊCH BẢN DRAMA & BÍ ẨN (~60 GIÂY)
# ==========================================
SCENES = [
    {
        "image": "dram1.jpg",
        "text": "Những gì sách giáo khoa dạy bạn về Kim Tự Tháp... có thể là một lời nói dối hoàn hảo!",
        "effect": "zoom_in_fast"
    },
    {
        "image": "dram2.jpg",
        "text": "Hai phẩy ba triệu khối cự thạch, nặng từ hai đến tám mươi tấn mỗi khối. Người cổ đại chỉ dùng búa đồng và dây thừng để vận chuyển qua hàng trăm cây số? Điều đó là hoàn toàn bất khả thi!",
        "effect": "pan_down"
    },
    {
        "image": "dram3.jpg",
        "text": "Kỳ lạ hơn nữa, bên trong Đại Kim Tự Tháp Giza chưa từng tìm thấy bất kỳ xác ướp pharaoh nào, cũng không hề có một dòng chữ tượng hình hay lời ca tụng lăng mộ!",
        "effect": "zoom_in_slow"
    },
    {
        "image": "dram4.jpg",
        "text": "Nhiều nhà khoa học hiện đại tin rằng: Cấu trúc đá granit chứa tinh thể thạch anh này thực chất là một trạm phát điện từ trường khổng lồ của một nền văn minh tiền sử đã biến mất!",
        "effect": "zoom_out"
    },
    {
        "image": "dram5.jpg",
        "text": "Kinh ngạc nhất, tọa độ địa lý chính xác của Kim Tự Tháp trùng khớp hoàn toàn với vận tốc ánh sáng: hai trăm chín mươi chín triệu bảy trăm chín mươi hai nghìn mét trên giây!",
        "effect": "zoom_in_slow"
    },
    {
        "image": "dram6.jpg",
        "text": "Nếu không phải con người thời đồ đồng xây dựng... thì thực sự ai mới là kẻ đã tạo ra chúng? Hãy để lại suy nghĩ của bạn!",
        "effect": "zoom_in_fast"
    }
]

# Giọng đọc Nam bí ẩn, đanh thép chuẩn phim tài liệu / drama
VOICE = "vi-VN-NamMinhNeural"
OUTPUT_VIDEO = "video_kim_tu_thap_drama_1min.mp4"
FPS = 30
WIDTH = 1080
HEIGHT = 1920

def get_audio_duration(audio_file):
    cmd = [FFMPEG_EXE, "-i", audio_file]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        hours, mins, secs = m.groups()
        return int(hours) * 3600 + int(mins) * 60 + float(secs)
    return 8.0

async def generate_voiceovers():
    print("[1/5] Đang tạo giọng đọc bí ẩn tiếng Việt (Nam Minh Neural)...")
    durations = []
    for idx, scene in enumerate(SCENES):
        audio_path = f"temp_dram_audio_{idx}.mp3"
        # Đọc với tốc độ chuẩn, nhấn nhá kịch tính
        comm = edge_tts.Communicate(scene["text"], VOICE, rate="-1%")
        await comm.save(audio_path)
        dur = get_audio_duration(audio_path)
        # Thêm 0.35s đệm ngắt nghỉ kịch tính giữa các cảnh
        padded_dur = dur + 0.35
        durations.append(padded_dur)
        print(f"   Cảnh {idx+1}: {padded_dur:.2f}s | {scene['text'][:55]}...")
    total_dur = sum(durations)
    print(f"-> Tổng thời lượng dự kiến: {total_dur:.1f} giây (~1 phút)")
    return durations

def create_cinematic_bgm(total_duration, output_wav="temp_bgm.wav"):
    """Tạo nhạc nền hiệu ứng âm thanh kịch tính: Sub-bass + Nhịp tim đập dồn dập + Âm thanh vũ trụ bí ẩn"""
    print(f"[2/5] Đang tổng hợp nhạc nền Tension/Suspense ({total_duration:.1f}s)...")
    sr = 44100
    t = np.linspace(0, total_duration, int(sr * total_duration), endpoint=False)

    # 1. Âm trầm Sub-bass rung rợn (55Hz và 110Hz)
    sub = 0.45 * np.sin(2 * np.pi * 55 * t) + 0.25 * np.sin(2 * np.pi * 110 * t)
    # Tần số dao động chậm tạo cảm giác ngột ngạt, hồi hộp
    swell = 0.65 + 0.35 * np.sin(2 * np.pi * 0.15 * t)

    # 2. Tiếng nhịp tim hồi hộp (Heartbeat 'thump-thump') mỗi 1.4 giây
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
    mystery = 0.07 * np.sin(2 * np.pi * 432 * t + 0.2 * np.sin(2 * np.pi * 0.4 * t))

    combined = (sub * swell + hb * 0.75 + mystery) * 0.45
    audio = np.int16(combined / (np.max(np.abs(combined)) + 1e-6) * 32767)

    with wave.open(output_wav, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(audio.tobytes())
    return output_wav

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

def create_ass_subtitles(durations, output_sub="temp_subtitles_drama.ass"):
    print("[3/5] Đang tạo tệp phụ đề phong cách vàng kim nổi bật...")
    # Màu &H0022E5FF là màu vàng hổ phách rực rỡ (Amber/Golden Yellow) chuẩn tài liệu bí ẩn
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: DramaDefault,Segoe UI,60,&H0020E0FF,&H000000FF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,1,5,3,2,70,70,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    current_time = 0.0
    dialogues = []
    for idx, (scene, dur) in enumerate(zip(SCENES, durations)):
        start = current_time
        end = current_time + dur
        
        words = scene["text"].split()
        if len(words) > 8:
            half = len(words) // 2
            formatted_text = " ".join(words[:half]) + "\\N" + " ".join(words[half:])
        else:
            formatted_text = scene["text"]
            
        dialogues.append(f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},DramaDefault,,0,0,0,,{formatted_text}")
        current_time = end

    with open(output_sub, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")
    return output_sub

def render_scene(idx, scene, duration):
    img = scene["image"]
    audio = f"temp_dram_audio_{idx}.mp3"
    out_clip = f"temp_dram_clip_{idx}.mp4"
    frames = int(duration * FPS)

    effect = scene["effect"]
    if effect == "zoom_in_fast":
        zoom_expr = "zoompan=z='min(zoom+0.0020,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_in_slow":
        zoom_expr = "zoompan=z='min(zoom+0.0012,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "zoom_out":
        zoom_expr = "zoompan=z='if(eq(on,1),1.3,max(1.0,zoom-0.0018))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif effect == "pan_down":
        zoom_expr = "zoompan=z=1.2:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom, on*0.65)'"
    else:
        zoom_expr = "zoompan=z='min(zoom+0.0015,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

    vf = f"{zoom_expr}:d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"

    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", img,
        "-i", audio,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_clip
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_clip

async def main():
    print("=====================================================")
    print("  BẮT ĐẦU SẢN XUẤT VIDEO DRAMA BÍ ẨN 1 PHÚT (AI SHORTS)")
    print("=====================================================")
    
    # 1. Tạo Giọng đọc
    durations = await generate_voiceovers()
    total_dur = sum(durations)

    # 2. Tạo Nhạc nền Tension
    bgm_file = create_cinematic_bgm(total_dur)

    # 3. Tạo Subtitles vàng kịch tính
    sub_file = create_ass_subtitles(durations)

    # 4. Render từng cảnh
    print("[4/5] Đang render chuyển động điện ảnh cho từng cảnh...")
    clip_files = []
    concat_list = "temp_dram_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for idx, scene in enumerate(SCENES):
            print(f"   Đang xử lý cảnh {idx+1}/{len(SCENES)}: {scene['effect']} ({durations[idx]:.1f}s)...")
            clip = render_scene(idx, scene, durations[idx])
            clip_files.append(clip)
            f.write(f"file '{clip}'\n")

    # 5. Ghép nối, Mix giọng đọc + Nhạc nền BGM + Phụ đề
    print(f"[5/5] Đang hòa âm giọng đọc + BGM và nung phụ đề vào: {OUTPUT_VIDEO}...")
    temp_concat_video = "temp_merged_raw.mp4"
    
    # 5.1 Concat các clip video
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy",
        temp_concat_video
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5.2 Hòa âm BGM vào video và nung Subtitles
    final_cmd = [
        FFMPEG_EXE, "-y",
        "-i", temp_concat_video,
        "-i", bgm_file,
        "-filter_complex",
        f"[0:v]subtitles={sub_file}[vsub];[0:a]volume=1.0[v_voice];[1:a]volume=0.25[v_bgm];[v_voice][v_bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[vsub]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        OUTPUT_VIDEO
    ]
    subprocess.run(final_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 6. Dọn dẹp tệp tạm
    print("Dọn dẹp các tệp tạm thời...")
    for f in clip_files:
        if os.path.exists(f): os.remove(f)
    for idx in range(len(SCENES)):
        aud = f"temp_dram_audio_{idx}.mp3"
        if os.path.exists(aud): os.remove(aud)
    for temp in [concat_list, sub_file, bgm_file, temp_concat_video]:
        if os.path.exists(temp): os.remove(temp)

    print(f"\n HOÀN TẤT! Video Drama 1 phút đã sẵn sàng tại:\n-> {os.path.abspath(OUTPUT_VIDEO)}")

if __name__ == "__main__":
    asyncio.run(main())
