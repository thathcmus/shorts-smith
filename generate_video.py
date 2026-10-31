#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Video Producer - CLI Entry Point (V2 Enhanced)
Sản xuất video AI chất lượng cao: Phụ đề TikTok Karaoke Dynamic, Nhạc nền MP3 điện ảnh, Color Grading & Vignette.
"""

import argparse
import asyncio
import os
import re
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
    DEFAULT_SPEECH_RATE,
    DEFAULT_PITCH,
    DEFAULT_FPS,
    OUTPUT_DIR,
    TEMP_DIR,
)
from engine.tts import synthesize_speech_with_words, generate_tiktok_style_subtitles
from engine.render import render_scene_clip, assemble_final_video, get_best_bgm_track
from engine.script_generator import (
    load_script_from_file,
    find_script_by_index_or_path,
    derive_default_output_name,
)
from engine.publisher import create_publish_workspace, get_next_sequence_prefix

async def run_pipeline(
    scenes: list,
    output_filename: str = None,
    voice: str = DEFAULT_VOICE,
    speech_rate: str = DEFAULT_SPEECH_RATE,
    pitch: str = DEFAULT_PITCH,
    aspect: str = "vertical",
    bgm_path: str = None,
    bgm_volume: float = 0.22
):
    start_time = time.time()
    width, height = RESOLUTIONS.get(aspect, RESOLUTIONS["vertical"])

    # Hỗ trợ alias viết tắt cho voice (vi_nu, vi_nam, hoaimy, namminh...)
    voice = VOICES.get(voice, voice)
    if voice.lower() in ["nu", "hoaimy", "hoai_my"]:
        voice = VOICES["vi_nu"]
    elif voice.lower() in ["nam", "namminh", "nam_minh"]:
        voice = VOICES["vi_nam"]

    # Tự động gắn tiền tố số thứ tự (001_, 002_...) nếu chưa có để đồng bộ 1:1 với Caption
    if not output_filename:
        seq = get_next_sequence_prefix(OUTPUT_DIR)
        timestamp = int(time.time())
        output_filename = f"{seq}_video_{timestamp}.mp4"
    else:
        m = re.match(r"^\d{2,4}_", output_filename)
        if not m:
            seq = get_next_sequence_prefix(OUTPUT_DIR)
            output_filename = f"{seq}_{output_filename}"

    output_video_path = os.path.join(OUTPUT_DIR, output_filename)
    job_temp_dir = os.path.join(TEMP_DIR, f"job_{int(time.time())}")
    os.makedirs(job_temp_dir, exist_ok=True)

    # Lựa chọn bản nhạc nền điện ảnh chất lượng cao
    selected_bgm = get_best_bgm_track(bgm_path)

    print("=================================================================")
    print(f"🎬 AI VIDEO PRODUCER V2 (TIKTOK DYNAMIC SUBTITLES & CINEMATIC AUDIO)")
    print(f"📐 Khung hình: {aspect.upper()} ({width}x{height})")
    print(f"🎙️ Giọng đọc: {voice} (Tốc độ: {speech_rate} | Cao độ Pitch: {pitch})")
    print(f"🎵 Nhạc nền BGM: {os.path.basename(selected_bgm) if selected_bgm else 'Không'}")
    print(f"📁 Xuất ra: {output_video_path}")
    print("=================================================================")

    # BƯỚC 1: Sinh giọng đọc thuyết minh & ghi nhận WordBoundary (từng từ)
    print("\n[1/5] 🎙️ Đang tổng hợp giọng thuyết minh và đồng bộ nhịp từ (Word-level sync)...")
    scenes_data = []
    audio_paths = []

    for idx, scene in enumerate(scenes):
        audio_file = os.path.join(job_temp_dir, f"audio_scene_{idx}.mp3")
        text = scene["text"]
        rate = scene.get("rate", speech_rate)
        cur_pitch = scene.get("pitch", pitch)
        cur_voice = VOICES.get(scene.get("voice", voice), scene.get("voice", voice))
        print(f"   - Cảnh {idx+1}/{len(scenes)} [{rate} | {cur_pitch}]: {text[:50]}...")

        dur, words = await synthesize_speech_with_words(text, audio_file, voice=cur_voice, rate=rate, pitch=cur_pitch)
        padded_dur = dur + 0.35  # Đệm ngắt nghỉ kịch tính giữa các cảnh
        
        scenes_data.append({
            "text": text,
            "duration": padded_dur,
            "words": words,
            "media": scene.get("media") or scene.get("image") or scene.get("video"),
            "effect": scene.get("effect", "zoom_in_slow")
        })
        audio_paths.append(audio_file)
        print(f"     Thời lượng: {padded_dur:.2f}s | {len(words)} từ được bắt nhịp")

    total_duration = sum(s["duration"] for s in scenes_data)
    print(f"-> Tổng thời lượng dự kiến: {total_duration:.1f} giây")

    # BƯỚC 2: Tạo phụ đề động TikTok Karaoke (Word-by-word Highlight)
    print("\n[2/5] ✨ Đang tạo tệp phụ đề TikTok Karaoke Dynamic (Vàng Neon / Trắng viền đen)...")
    sub_path = os.path.join(job_temp_dir, "tiktok_karaoke.ass")
    generate_tiktok_style_subtitles(scenes_data, sub_path, width=width, height=height)

    # BƯỚC 3: Render từng cảnh với hiệu ứng Ken Burns + Color Grading + Vignette
    print("\n[3/5] 🎥 Đang render từng cảnh điện ảnh (Ken Burns + Color Grade + Vignette)...")
    clip_paths = []
    for idx, item in enumerate(scenes_data):
        clip_file = os.path.join(job_temp_dir, f"clip_scene_{idx}.mp4")
        media = item["media"]
        print(f"   - Cảnh {idx+1}: {item['effect']} ({item['duration']:.1f}s) từ nguồn: {media}...")
        render_scene_clip(
            media_path=media,
            audio_path=audio_paths[idx],
            output_clip_path=clip_file,
            duration=item["duration"],
            effect=item["effect"],
            width=width,
            height=height,
            fps=DEFAULT_FPS
        )
        clip_paths.append(clip_file)

    # BƯỚC 4: Ghép nối, hòa âm BGM điện ảnh và nung phụ đề TikTok
    print(f"\n[4/5] ⚡ Đang hòa âm BGM điện ảnh, nung phụ đề động vào: {output_filename}...")
    assemble_final_video(
        clip_paths=clip_paths,
        output_video_path=output_video_path,
        bgm_path=selected_bgm,
        subtitles_path=sub_path,
        bgm_volume=bgm_volume,
        temp_dir=job_temp_dir
    )

    # BƯỚC 5: Đóng gói không gian xuất bản TikTok & Caption (output/cap và output/publish_packages)
    print(f"\n[5/5] 📦 Đang đóng gói không gian xuất bản TikTok (Caption + Thumbnail)...")
    pub_info = create_publish_workspace(
        video_path=output_video_path,
        scenes=scenes,
        duration=total_duration
    )

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    print("\n=================================================================")
    print(f"✅ HOÀN TẤT TRONG {elapsed:.1f} GIÂY!")
    print(f"🎉 Tệp video: {output_video_path} ({file_size_mb:.2f} MB)")
    print(f"📝 Caption TikTok: {pub_info['cap_file']}")
    print(f"🖼️ Ảnh bìa Cover: {pub_info['cover_file']}")
    print(f"📦 Thư mục trọn gói: {pub_info['package_dir']}")
    print("=================================================================")
    return output_video_path

def main():
    parser = argparse.ArgumentParser(description="AI Video Producer V2 CLI")
    parser.add_argument("--script", "-s", type=str, help="Index số (ví dụ: 001, 3, 4...), từ khóa slug hoặc đường dẫn tệp JSON kịch bản")
    parser.add_argument("--voice", "-v", type=str, default=DEFAULT_VOICE, help="Tên giọng đọc Edge-TTS (vi_nam, vi_nu, vi-VN-HoaiMyNeural...)")
    parser.add_argument("--rate", "-r", type=str, default=DEFAULT_SPEECH_RATE, help="Tốc độ giọng đọc (+50%% tương đương 1.5x, ví dụ: +0%%, +25%%, +50%%)")
    parser.add_argument("--pitch", "-p", type=str, default=DEFAULT_PITCH, help="Cao độ giọng đọc (+0Hz, -6Hz trầm u tối, +5Hz thanh cao)")
    parser.add_argument("--bgm", "-b", type=str, default=None, help="Đường dẫn tệp nhạc nền MP3 riêng")
    parser.add_argument("--output", "-o", type=str, default=None, help="Tên tệp xuất MP4")
    parser.add_argument("--aspect", "-a", type=str, default="vertical", choices=["vertical", "horizontal"], help="Tỉ lệ: vertical (9:16) hoặc horizontal (16:9)")
    parser.add_argument("--bgm-volume", type=float, default=0.22, help="Âm lượng nhạc nền (0.0 đến 1.0)")
    args = parser.parse_args()

    # Phân giải kịch bản theo index số (001, 3, 4...), slug hoặc đường dẫn file
    try:
        script_file = find_script_by_index_or_path(args.script)
    except FileNotFoundError as e:
        print(f"\n{e}")
        sys.exit(1)

    if not script_file or not os.path.exists(script_file):
        print(f"❌ Không tìm thấy tệp kịch bản nào phù hợp với: '{args.script}'")
        sys.exit(1)

    print(f"📖 Đang tải kịch bản: {script_file}")
    scenes = load_script_from_file(script_file)

    # Tự động suy luận tên tệp video xuất ra nếu chưa chỉ định --output
    output_filename = args.output
    if not output_filename and script_file:
        output_filename = derive_default_output_name(script_file)
        if output_filename:
            print(f"🎯 Tự động đặt tên video xuất ra: {output_filename}")

    asyncio.run(run_pipeline(
        scenes=scenes,
        output_filename=output_filename,
        voice=args.voice,
        speech_rate=args.rate,
        pitch=args.pitch,
        aspect=args.aspect,
        bgm_path=args.bgm,
        bgm_volume=args.bgm_volume
    ))

if __name__ == "__main__":
    main()
