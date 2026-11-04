#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Video Producer - CLI Entry Point (V2.5 Enhanced)
Sản xuất video AI chất lượng cao: Tự động hóa tài nguyên đầu vào từ chủ đề (Topic),
tải song song 6 ảnh AI đám mây miễn phí, Phụ đề TikTok Karaoke Dynamic,
Nhạc nền MP3 điện ảnh, Color Grading & Vignette, và dọn dẹp tài nguyên an toàn.
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
    BASE_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
)
from engine.tts import synthesize_speech_with_words, generate_tiktok_style_subtitles
from engine.render import (
    render_scene_clip,
    assemble_final_video,
    get_best_bgm_track,
    clean_temp_files
)
from engine.image_generator import generate_images_parallel, validate_image_file
from engine.script_generator import (
    load_script_from_file,
    save_script_to_file,
    find_script_by_index_or_path,
    derive_default_output_name,
    generate_script_from_topic
)
from engine.publisher import create_publish_workspace, get_next_sequence_prefix

def slugify_text(text: str) -> str:
    """Chuyển đổi tiêu đề thành slug không dấu an toàn cho tên file."""
    t = text.lower().strip()
    replacements = (
        ("á|à|ả|ã|ạ|ă|ắ|ằ|ẳ|ẵ|ặ|â|ấ|ầ|ẩ|ẫ|ậ", "a"),
        ("é|è|ẻ|ẽ|ẹ|ê|ế|ề|ể|ễ|ệ", "e"),
        ("i|í|ì|ỉ|ĩ|ị", "i"),
        ("ó|ò|ỏ|õ|ọ|ô|ố|ồ|ổ|ỗ|ộ|ơ|ớ|ờ|ở|ỡ|ợ", "o"),
        ("ú|ù|ủ|ũ|ụ|ư|ứ|ừ|ử|ữ|ự", "u"),
        ("ý|ỳ|ỷ|ỹ|ỵ", "y"),
        ("đ", "d"),
    )
    for pat, rep in replacements:
        t = re.sub(pat, rep, t)
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_")[:40] or "video"

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

    try:
        # Lựa chọn bản nhạc nền điện ảnh chất lượng cao
        selected_bgm = get_best_bgm_track(bgm_path)

        print("=================================================================")
        print(f"🎬 AI VIDEO PRODUCER V2.5 (AUTOMATED INPUT & CINEMATIC PIPELINE)")
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
        file_size_mb = os.path.getsize(output_video_path) / (1024 * 1024) if os.path.exists(output_video_path) else 0.0
        print("\n=================================================================")
        print(f"✅ HOÀN TẤT TRONG {elapsed:.1f} GIÂY!")
        print(f"🎉 Tệp video: {output_video_path} ({file_size_mb:.2f} MB)")
        print(f"📝 Caption TikTok: {pub_info.get('cap_file')}")
        print(f"🖼️ Ảnh bìa Cover: {pub_info.get('cover_file')}")
        print(f"📦 Thư mục trọn gói: {pub_info.get('package_dir')}")
        print("=================================================================")
        return output_video_path
    finally:
        # Tự động dọn dẹp thư mục tạm thời của job và dọn file rác mồ côi
        clean_temp_files(job_dir=job_temp_dir)

def create_placeholder_frame(
    output_path: str,
    scene_idx: int,
    total_scenes: int,
    title: str,
    prompt: str = "",
    width: int = 1080,
    height: int = 1920
):
    """Tự động sinh ảnh giữ chỗ 9:16 điện ảnh (placeholder) khi chưa có ảnh thật."""
    from PIL import Image, ImageDraw
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Deep slate navy
    draw = ImageDraw.Draw(img)

    draw.rectangle([40, 40, width - 40, height - 40], outline=(0, 229, 255), width=4)

    badge_text = f"CẢNH {scene_idx}/{total_scenes} (ẢNH GIỮ CHỖ TẠM THỜI)"
    draw.text((width // 2, 550), badge_text, fill=(255, 230, 0), anchor="mm")

    clean_title = title if len(title) <= 120 else title[:120] + "..."
    words = clean_title.split()
    lines = []
    cur_line = []
    for w in words:
        cur_line.append(w)
        if len(" ".join(cur_line)) > 26:
            lines.append(" ".join(cur_line))
            cur_line = []
    if cur_line:
        lines.append(" ".join(cur_line))

    y = 700
    for l in lines[:5]:
        draw.text((width // 2, y), l, fill=(255, 255, 255), anchor="mm")
        y += 55

    if prompt:
        hint_clean = prompt if len(prompt) < 140 else prompt[:140] + "..."
        draw.text((width // 2, 1200), "PROMPT TẠO ẢNH:", fill=(0, 229, 255), anchor="mm")
        draw.text((width // 2, 1260), hint_clean, fill=(148, 163, 184), anchor="mm")

    img.save(output_path, quality=90)

def main():
    parser = argparse.ArgumentParser(description="AI Video Producer V2.5 CLI")
    parser.add_argument("--script", "-s", "--s", type=str, help="Index số (ví dụ: 001, 3, 4...), từ khóa slug hoặc đường dẫn tệp JSON kịch bản")
    parser.add_argument("--topic", "-t", type=str, default=None, help="Chủ đề video tự động sinh kịch bản và ảnh AI trọn gói (ví dụ: 'Kim Tự Tháp Rừng Amazon')")
    parser.add_argument("--generate-images", "-g", action="store_true", help="Ép buộc tải lại toàn bộ ảnh AI qua API đám mây ngay cả khi đã có sẵn tệp ảnh")
    parser.add_argument("--voice", "-v", type=str, default=DEFAULT_VOICE, help="Tên giọng đọc Edge-TTS (vi_nam, vi_nu, vi-VN-HoaiMyNeural...)")
    parser.add_argument("--rate", "-r", type=str, default=DEFAULT_SPEECH_RATE, help="Tốc độ giọng đọc (+50%% tương đương 1.5x, ví dụ: +0%%, +25%%, +50%%)")
    parser.add_argument("--pitch", "-p", type=str, default=DEFAULT_PITCH, help="Cao độ giọng đọc (+0Hz, -6Hz trầm u tối, +5Hz thanh cao)")
    parser.add_argument("--bgm", "-b", type=str, default=None, help="Đường dẫn tệp nhạc nền MP3 riêng")
    parser.add_argument("--output", "-o", type=str, default=None, help="Tên tệp xuất MP4")
    parser.add_argument("--aspect", "-a", type=str, default="vertical", choices=["vertical", "horizontal"], help="Tỉ lệ: vertical (9:16) hoặc horizontal (16:9)")
    parser.add_argument("--bgm-volume", type=float, default=0.22, help="Âm lượng nhạc nền (0.0 đến 1.0)")
    parser.add_argument("--placeholder", action="store_true", help="Tự động tạo ảnh giữ chỗ (placeholder 1080x1920) nếu thiếu ảnh")
    args = parser.parse_args()

    width, height = RESOLUTIONS.get(args.aspect, RESOLUTIONS["vertical"])
    output_filename = args.output

    # LUỒNG 1: Sinh tự động từ Chủ đề (--topic)
    if args.topic:
        print("\n" + "=" * 65)
        print(f"🤖 ĐANG TỰ ĐỘNG KHỞI TẠO NỘI DUNG TỪ CHỦ ĐỀ: '{args.topic}'")
        print("=" * 65)
        
        script_data = generate_script_from_topic(args.topic)
        scenes = script_data.get("scenes", [])
        
        seq = get_next_sequence_prefix(OUTPUT_DIR)
        slug = slugify_text(args.topic)
        script_file = os.path.join(BASE_DIR, "examples", f"{seq}_script_{slug}.json")
        asset_dir = os.path.join(BASE_DIR, "sample_assets", f"{seq}_{slug}")
        
        print(f"✨ Kịch bản 6 cảnh đã được tạo. Đang tải song song 6 ảnh AI (Pollinations FLUX 9:16)...")
        asyncio.run(generate_images_parallel(scenes, asset_dir, prefix=f"{seq}_{slug}", width=width, height=height))
        
        # Lưu kịch bản hoàn chỉnh kèm đường dẫn ảnh
        save_script_to_file(scenes, script_file)
        print(f"💾 Kịch bản đã lưu: {script_file}")
        
        if not output_filename:
            output_filename = f"{seq}_video_{slug}.mp4"

    # LUỒNG 2: Chạy từ kịch bản có sẵn (--script)
    else:
        try:
            script_file = find_script_by_index_or_path(args.script)
        except FileNotFoundError as e:
            print(f"\n{e}")
            sys.exit(1)

        if not script_file or not os.path.exists(script_file):
            print(f"❌ Không tìm thấy tệp kịch bản nào phù hợp với: '{args.script}'")
            print("💡 Bạn có thể chạy với cờ --topic để tự động sinh video từ chủ đề, ví dụ:")
            print("   python generate_video.py --topic 'Kim Tự Tháp Rừng Amazon'")
            sys.exit(1)

        print(f"📖 Đang tải kịch bản: {script_file}")
        scenes = load_script_from_file(script_file)

        # Kiểm tra ảnh thiếu hoặc cờ ép tải ảnh --generate-images
        missing_assets = []
        for idx, sc in enumerate(scenes):
            m_path = sc.get("media") or sc.get("image") or sc.get("video")
            if args.generate_images or not m_path or not os.path.exists(m_path) or not validate_image_file(m_path):
                missing_assets.append((idx + 1, sc))

        if missing_assets:
            base_script_name = os.path.splitext(os.path.basename(script_file))[0]
            m_seq = re.match(r"^(\d{2,4})_(.*)$", base_script_name)
            slug = m_seq.group(2) if m_seq else base_script_name
            asset_dir = os.path.join(BASE_DIR, "sample_assets", slug)
            
            # Nếu các cảnh có prompt tiếng Anh, tự động tải qua Cloud AI
            has_prompts = any(sc.get("prompt") for _, sc in missing_assets)
            if has_prompts:
                print(f"\n🎨 Đang tự động tải song song {len(missing_assets)} ảnh AI còn thiếu qua Pollinations FLUX...")
                asyncio.run(generate_images_parallel(scenes, asset_dir, prefix=slug, width=width, height=height))
                save_script_to_file(scenes, script_file)
                print("✅ Đã hoàn tất tải ảnh AI vào thư mục tài nguyên!")
            elif args.placeholder:
                print(f"\n🎨 Đang tạo ảnh giữ chỗ tạm thời (--placeholder)...")
                for sc_num, sc in missing_assets:
                    m_path = sc.get("image") or os.path.join(asset_dir, f"{slug}_{sc_num}.jpg")
                    sc["image"] = m_path
                    create_placeholder_frame(m_path, sc_num, len(scenes), sc.get("text", ""), sc.get("prompt", ""), width=width, height=height)
            else:
                print(f"❌ Kịch bản thiếu tệp ảnh. Vui lòng thêm prompt vào kịch bản hoặc chạy với cờ --generate-images / --placeholder.")
                sys.exit(1)

        if not output_filename and script_file:
            output_filename = derive_default_output_name(script_file)

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
