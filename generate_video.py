#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Video Producer - CLI Entry Point
Quy trình sản xuất video AI tự động chất lượng cao.
"""

import argparse
import asyncio
import os
import sys
import time

# Đảm bảo console Windows hỗ trợ UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.config import (
    RESOLUTIONS,
    VOICES,
    DEFAULT_VOICE,
    DEFAULT_FPS,
    OUTPUT_DIR,
    TEMP_DIR,
)
from engine.tts import synthesize_speech, generate_ass_subtitles
from engine.render import render_scene_clip, create_tension_bgm, assemble_final_video
from engine.script_generator import load_script_from_file

async def run_pipeline(
    scenes: list,
    output_filename: str = None,
    voice: str = DEFAULT_VOICE,
    aspect: str = "vertical",
    bgm_volume: float = 0.22
):
    start_time = time.time()
    width, height = RESOLUTIONS.get(aspect, RESOLUTIONS["vertical"])
    
    if not output_filename:
        timestamp = int(time.time())
        output_filename = f"ai_video_{timestamp}.mp4"
    
    output_video_path = os.path.join(OUTPUT_DIR, output_filename)
    job_temp_dir = os.path.join(TEMP_DIR, f"job_{int(time.time())}")
    os.makedirs(job_temp_dir, exist_ok=True)

    print("=================================================================")
    print(f"🎬 AI VIDEO PRODUCER: BẮT ĐẦU SẢN XUẤT VIDEO ({aspect.upper()} {width}x{height})")
    print(f"🔊 Giọng đọc: {voice}")
    print(f"📁 Xuất ra: {output_video_path}")
    print("=================================================================")

    # BƯỚC 1: Sinh giọng đọc thuyết minh & tính thời lượng từng cảnh
    print("\n[1/5] 🎙️ Đang tổng hợp giọng thuyết minh qua Edge-TTS...")
    scenes_data = []
    audio_paths = []
    
    for idx, scene in enumerate(scenes):
        audio_file = os.path.join(job_temp_dir, f"audio_scene_{idx}.mp3")
        text = scene["text"]
        rate = scene.get("rate", "-1%")
        print(f"   - Cảnh {idx+1}/{len(scenes)}: {text[:50]}...")
        
        dur = await synthesize_speech(text, audio_file, voice=voice, rate=rate)
        # Thêm 0.3s đệm kịch tính cho mỗi cảnh
        padded_dur = dur + 0.30
        scenes_data.append({
            "text": text,
            "duration": padded_dur,
            "image": scene["image"],
            "effect": scene.get("effect", "zoom_in_slow")
        })
        audio_paths.append(audio_file)
        print(f"     Thời lượng: {padded_dur:.2f}s")

    total_duration = sum(s["duration"] for s in scenes_data)
    print(f"-> Tổng thời lượng dự kiến: {total_duration:.1f} giây")

    # BƯỚC 2: Tạo nhạc nền BGM kịch tính (Cinematic Tension)
    print("\n[2/5] 🎵 Đang tổng hợp nhạc nền Tension/Suspense chuẩn xác...")
    bgm_path = os.path.join(job_temp_dir, "cinematic_bgm.wav")
    create_tension_bgm(total_duration, bgm_path)

    # BƯỚC 3: Tạo phụ đề vàng hoàng kim (Amber Gold Subtitles)
    print("\n[3/5] 📝 Đang tạo tệp phụ đề điện ảnh (.ass)...")
    sub_path = os.path.join(job_temp_dir, "subtitles.ass")
    generate_ass_subtitles(scenes_data, sub_path, width=width, height=height)

    # BƯỚC 4: Render từng cảnh với chuyển động Ken Burns
    print("\n[4/5] 🎥 Đang render hiệu ứng camera Ken Burns cho từng cảnh...")
    clip_paths = []
    for idx, item in enumerate(scenes_data):
        clip_file = os.path.join(job_temp_dir, f"clip_scene_{idx}.mp4")
        print(f"   - Đang render cảnh {idx+1}: {item['effect']} ({item['duration']:.1f}s)...")
        render_scene_clip(
            image_path=item["image"],
            audio_path=audio_paths[idx],
            output_clip_path=clip_file,
            duration=item["duration"],
            effect=item["effect"],
            width=width,
            height=height,
            fps=DEFAULT_FPS
        )
        clip_paths.append(clip_file)

    # BƯỚC 5: Ghép nối, hòa âm BGM và nung phụ đề
    print(f"\n[5/5] ⚡ Đang ghép nối, hòa âm (Audio Ducking) và xuất video: {output_filename}...")
    assemble_final_video(
        clip_paths=clip_paths,
        output_video_path=output_video_path,
        bgm_path=bgm_path,
        subtitles_path=sub_path,
        bgm_volume=bgm_volume,
        temp_dir=job_temp_dir
    )

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print("\n=================================================================")
    print(f"✅ HOÀN TẤT TRONG {elapsed:.1f} GIÂY!")
    print(f"🎉 Tệp video: {output_video_path} ({file_size_mb:.2f} MB)")
    print("=================================================================")
    return output_video_path

def main():
    parser = argparse.ArgumentParser(description="AI Video Producer CLI")
    parser.add_argument("--script", "-s", type=str, help="Đường dẫn tệp JSON kịch bản (nếu có)")
    parser.add_argument("--voice", "-v", type=str, default=DEFAULT_VOICE, help="Tên giọng đọc Edge-TTS")
    parser.add_argument("--output", "-o", type=str, default=None, help="Tên tệp xuất MP4")
    parser.add_argument("--aspect", "-a", type=str, default="vertical", choices=["vertical", "horizontal"], help="Tỉ lệ: vertical (9:16) hoặc horizontal (16:9)")
    parser.add_argument("--bgm-volume", type=float, default=0.22, help="Âm lượng nhạc nền (0.0 đến 1.0)")
    args = parser.parse_args()

    # Nếu có file kịch bản truyền vào
    if args.script and os.path.exists(args.script):
        scenes = load_script_from_file(args.script)
    else:
        # Kịch bản mặc định thử nghiệm mẫu
        scenes = [
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

    asyncio.run(run_pipeline(
        scenes=scenes,
        output_filename=args.output,
        voice=args.voice,
        aspect=args.aspect,
        bgm_volume=args.bgm_volume
    ))

if __name__ == "__main__":
    main()
