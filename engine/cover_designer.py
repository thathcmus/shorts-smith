"""
Mô-đun thiết kế ảnh bìa TikTok chuyên nghiệp (TikTok Cover Designer).
Tự động trích xuất frame đắt giá hoặc nhận ảnh đầu vào, phủ tiêu đề Typography chuẩn Clickbait TikTok
(Font chữ đậm, tương phản cao, viền bóng mờ / Badge nền, căn chỉnh trong Safe Zone 9:16).
Đồng bộ trực tiếp ra output/covers/ và output/publish_packages/.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from engine.config import FFMPEG_EXE, BASE_DIR, OUTPUT_DIR
from engine.publisher import COVERS_DIR, PACKAGES_DIR, parse_sequence_and_slug

# Kích thước chuẩn video dọc TikTok / Reels / Shorts
COVER_WIDTH = 1080
COVER_HEIGHT = 1920

# Safe Zone chuẩn TikTok:
# Tránh thanh công cụ trên (0 - 15%), tránh avatar/like bên phải (85 - 100%),
# tránh thanh mô tả/âm thanh bên dưới (75 - 100%).
# Vùng vàng đặt Tiêu đề bìa đập vào mắt người lướt là: Y từ 32% đến 48% chiều cao.

FONTS_SEARCH_PATHS = [
    r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold (Hỗ trợ 100% tiếng Việt)
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\tahomabd.ttf",  # Tahoma Bold
    r"C:\Windows\Fonts\impact.ttf",    # Impact (Dự phòng)
]

def get_best_font(size: int = 72) -> ImageFont.FreeTypeFont:
    """Tìm font đậm hỗ trợ unicode tiếng Việt tốt nhất trên hệ thống."""
    for p in FONTS_SEARCH_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def extract_frame_for_cover(video_path: str, timestamp_sec: float = 2.5) -> Image.Image:
    """Trích xuất 1 frame chất lượng cao từ video làm nền ảnh bìa."""
    temp_frame = os.path.join(OUTPUT_DIR, f"temp_cover_extract_{os.getpid()}.jpg")
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", str(timestamp_sec),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        temp_frame
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_frame):
        img = Image.open(temp_frame).convert("RGB")
        try:
            os.remove(temp_frame)
        except Exception:
            pass
        return img
    # Nếu không trích xuất được, tạo canvas tối màu
    return Image.new("RGB", (COVER_WIDTH, COVER_HEIGHT), (20, 20, 25))

def create_tiktok_cover(
    background_source: str, # Có thể là file video .mp4, file ảnh .jpg/.png, hoặc None
    title: str,
    subtitle: str = None,
    badge_text: str = None,
    timestamp_sec: float = 2.5,
    style: str = "neon_yellow", # neon_yellow, fire_red, clean_white
    output_path: str = None
) -> str:
    """
    Tạo ảnh bìa 9:16 (1080x1920) chuẩn phong cách TikTok Viral Thumbnail:
    - background_source: Đường dẫn video hoặc ảnh nền
    - title: Tiêu đề giật gân (2-5 từ viết hoa, ví dụ: "INTERNET ĐÃ CHẾT?")
    - subtitle: Dòng giải thích ngắn (ví dụ: "BÍ MẬT 90% LÀ BOT AI")
    - badge_text: Tag nổi bật ở trên cùng (ví dụ: "SỰ THẬT", "BÍ ẨN KHOA HỌC")
    - style: Tông màu chủ đạo (neon_yellow, fire_red, clean_white)
    """
    # 1. Chuẩn bị ảnh nền
    if background_source and os.path.exists(background_source):
        ext = os.path.splitext(background_source)[1].lower()
        if ext in [".mp4", ".mov", ".mkv", ".avi"]:
            bg_img = extract_frame_for_cover(background_source, timestamp_sec)
        else:
            bg_img = Image.open(background_source).convert("RGB")
    else:
        bg_img = Image.new("RGB", (COVER_WIDTH, COVER_HEIGHT), (25, 25, 30))

    # Resize & Crop về chuẩn 1080x1920
    bg_w, bg_h = bg_img.size
    target_ratio = COVER_WIDTH / COVER_HEIGHT
    current_ratio = bg_w / bg_h

    if current_ratio > target_ratio:
        new_w = int(bg_h * target_ratio)
        offset = (bg_w - new_w) // 2
        bg_img = bg_img.crop((offset, 0, offset + new_w, bg_h))
    else:
        new_h = int(bg_w / target_ratio)
        offset = (bg_h - new_h) // 2
        bg_img = bg_img.crop((0, offset, bg_w, offset + new_h))

    bg_img = bg_img.resize((COVER_WIDTH, COVER_HEIGHT), Image.Resampling.LANCZOS)

    # Thêm lớp tối nhẹ để chữ nổi bật hơn
    overlay = Image.new("RGBA", (COVER_WIDTH, COVER_HEIGHT), (0, 0, 0, 60))
    bg_img = Image.alpha_composite(bg_img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(bg_img)

    # 2. Bảng màu theo style
    styles = {
        "neon_yellow": {
            "title_fill": (255, 230, 0),     # Vàng Neon
            "subtitle_fill": (255, 255, 255), # Trắng
            "badge_bg": (255, 40, 40),        # Đỏ tươi
            "badge_fill": (255, 255, 255),
            "stroke_color": (0, 0, 0),
            "stroke_width": 7
        },
        "fire_red": {
            "title_fill": (255, 45, 45),      # Đỏ cảnh báo
            "subtitle_fill": (255, 230, 0),   # Vàng
            "badge_bg": (0, 0, 0),
            "badge_fill": (255, 255, 255),
            "stroke_color": (0, 0, 0),
            "stroke_width": 7
        },
        "clean_white": {
            "title_fill": (255, 255, 255),    # Trắng sáng
            "subtitle_fill": (255, 230, 0),   # Vàng
            "badge_bg": (0, 140, 255),        # Xanh dương
            "badge_fill": (255, 255, 255),
            "stroke_color": (0, 0, 0),
            "stroke_width": 7
        }
    }
    cfg = styles.get(style, styles["neon_yellow"])

    # 3. Tính toán vị trí Safe Zone (Y khoảng 650 đến 850px)
    start_y = int(COVER_HEIGHT * 0.35)
    center_x = COVER_WIDTH // 2

    # A. Vẽ Badge Tag (nếu có)
    if badge_text:
        badge_font = get_best_font(42)
        badge_text_clean = f"  {badge_text.upper().strip()}  "
        bbox = draw.textbbox((0, 0), badge_text_clean, font=badge_font)
        bw = bbox[2] - bbox[0] + 30
        bh = bbox[3] - bbox[1] + 18
        bx1 = center_x - bw // 2
        by1 = start_y - bh - 25
        # Vẽ hộp bo góc cho badge
        draw.rounded_rectangle([bx1, by1, bx1 + bw, by1 + bh], radius=12, fill=cfg["badge_bg"])
        draw.text((center_x, by1 + bh // 2), badge_text_clean, font=badge_font,
                  fill=cfg["badge_fill"], anchor="mm")

    # B. Xử lý và ngắt dòng Title chính
    title_font_size = 80 if len(title) > 20 else 92
    title_font = get_best_font(title_font_size)
    title_text = title.upper().strip()

    # Tự động chia dòng nếu title dài
    words = title_text.split()
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        test_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_str, font=title_font)
        if bbox[2] - bbox[0] > COVER_WIDTH - 120 and len(current_line) > 1:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))

    # Vẽ nền hộp mờ (Dark Box Pill) phía sau cụm chữ chính để cực kỳ dễ đọc
    total_text_h = len(lines) * (title_font_size + 20)
    if subtitle:
        total_text_h += 80

    box_pad_x = 40
    box_pad_y = 30
    box_top = start_y - box_pad_y
    box_bottom = start_y + total_text_h + box_pad_y
    box_left = 40
    box_right = COVER_WIDTH - 40

    # Vẽ hộp mờ bán trong suốt
    box_overlay = Image.new("RGBA", (COVER_WIDTH, COVER_HEIGHT), (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box_overlay)
    box_draw.rounded_rectangle(
        [box_left, box_top, box_right, box_bottom],
        radius=24,
        fill=(0, 0, 0, 180) # Đen mờ 70%
    )
    bg_img = Image.alpha_composite(bg_img.convert("RGBA"), box_overlay).convert("RGB")
    draw = ImageDraw.Draw(bg_img)

    # Vẽ từng dòng của Tiêu đề
    curr_y = start_y + 10
    for line in lines:
        draw.text(
            (center_x, curr_y),
            line,
            font=title_font,
            fill=cfg["title_fill"],
            anchor="mt",
            stroke_width=cfg["stroke_width"],
            stroke_fill=cfg["stroke_color"]
        )
        curr_y += title_font_size + 18

    # C. Vẽ Subtitle (Dòng phụ)
    if subtitle:
        curr_y += 10
        sub_font = get_best_font(50)
        sub_text = subtitle.upper().strip()
        draw.text(
            (center_x, curr_y),
            sub_text,
            font=sub_font,
            fill=cfg["subtitle_fill"],
            anchor="mt",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )

    # 4. Lưu ảnh kết quả
    if not output_path:
        output_path = os.path.join(COVERS_DIR, "custom_cover.jpg")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    bg_img.save(output_path, "JPEG", quality=95)
    return output_path

def design_cover_for_video_id(
    video_id: str,
    title: str,
    subtitle: str = None,
    badge: str = None,
    style: str = "neon_yellow",
    timestamp_sec: float = 2.5
) -> dict:
    """
    Thiết kế và cập nhật ảnh bìa cho video đã tồn tại dựa theo ID hoặc Slug (ví dụ: '001' hoặc '002').
    Tự động cập nhật vào:
      1. output/covers/{seq}_cover_{slug}.jpg
      2. output/publish_packages/{seq}_{slug}/{seq}_cover_{slug}.jpg
      3. output/publish_packages/{seq}_{slug}/{seq}_metadata.json
    """
    # Tìm package phù hợp
    clean_id = video_id.strip()
    target_pkg = None
    if os.path.exists(PACKAGES_DIR):
        for pkg in os.listdir(PACKAGES_DIR):
            if pkg.startswith(clean_id) or clean_id in pkg:
                target_pkg = os.path.join(PACKAGES_DIR, pkg)
                break

    if not target_pkg:
        raise FileNotFoundError(f"Không tìm thấy video nào có mã số hoặc tên: '{video_id}' trong {PACKAGES_DIR}")

    pkg_name = os.path.basename(target_pkg)
    m = re.match(r"^(\d{2,4})_(.*)$", pkg_name)
    seq = m.group(1) if m else "000"
    slug = m.group(2) if m else pkg_name

    # Tìm file video trong package
    vids = glob.glob(os.path.join(target_pkg, "*.mp4"))
    video_source = vids[0] if vids else None

    # Tự động tìm ảnh gốc sạch (để không bao giờ bị dính chữ phụ đề / câu thoại nung trên video)
    clean_bg = None

    # Cách 1: Tìm qua kịch bản JSON (bằng find_script_by_index_or_path hoặc quét thư mục examples/)
    from engine.script_generator import find_script_by_index_or_path
    sc_file = None
    for target in [seq, slug, f"{seq}_{slug}"]:
        try:
            sc_file = find_script_by_index_or_path(target)
            if sc_file and os.path.exists(sc_file):
                break
        except Exception:
            pass

    if sc_file and os.path.exists(sc_file):
        try:
            with open(sc_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
            scenes = sdata.get("scenes", [])
            for sc in scenes:
                img_cand = sc.get("image") or sc.get("media")
                if img_cand:
                    full_p = os.path.join(BASE_DIR, img_cand) if not os.path.isabs(img_cand) else img_cand
                    if os.path.exists(full_p):
                        clean_bg = full_p
                        break
        except Exception:
            pass

    # Cách 2: Tìm trực tiếp trong sample_assets/
    if not clean_bg:
        asset_patterns = [
            f"{seq}_{slug}_1.jpg",
            f"{seq}_{slug}.jpg",
            f"{seq}_*1.jpg",
            f"{slug}_1.jpg",
            f"{slug}.jpg",
            f"*{slug}*1.jpg",
            f"*{slug}*.jpg",
        ]
        for pat in asset_patterns:
            matches = glob.glob(os.path.join(BASE_DIR, "sample_assets", pat))
            if matches:
                clean_bg = matches[0]
                break

    bg_source = clean_bg if clean_bg else video_source
    if clean_bg:
        print(f"🌟 Sử dụng ảnh gốc sạch KHÔNG dính phụ đề/thoại: {os.path.basename(clean_bg)}")
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy ảnh gốc sạch, buộc phải trích xuất từ video (có thể dính phụ đề)")

    # Tên file ảnh bìa chuẩn
    cover_filename = f"{seq}_cover_{slug}.jpg"
    top_cover_path = os.path.join(COVERS_DIR, cover_filename)
    pkg_cover_path = os.path.join(target_pkg, cover_filename)

    # Tạo ảnh bìa
    create_tiktok_cover(
        background_source=bg_source,
        title=title,
        subtitle=subtitle,
        badge_text=badge,
        timestamp_sec=timestamp_sec,
        style=style,
        output_path=top_cover_path
    )

    # Đồng bộ sang package
    shutil.copy2(top_cover_path, pkg_cover_path)

    # Cập nhật metadata nếu có
    meta_files = glob.glob(os.path.join(target_pkg, "*metadata.json"))
    if meta_files:
        try:
            with open(meta_files[0], "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["custom_cover_title"] = title
            meta["custom_cover_subtitle"] = subtitle
            meta["custom_cover_style"] = style
            with open(meta_files[0], "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    return {
        "sequence": seq,
        "slug": slug,
        "cover_top": top_cover_path,
        "cover_pkg": pkg_cover_path,
        "title": title,
        "subtitle": subtitle
    }

def main():
    parser = argparse.ArgumentParser(description="TikTok Cover & Thumbnail Designer CLI")
    parser.add_argument("--id", help="Số thứ tự video (ví dụ: 001, 002) để cập nhật ảnh bìa trực tiếp")
    parser.add_argument("--video", "-v", help="Đường dẫn file video MP4 nguồn")
    parser.add_argument("--image", "-i", help="Đường dẫn file ảnh nền nguồn")
    parser.add_argument("--title", "-t", required=True, help="Tiêu đề giật gân chính (ví dụ: 'INTERNET ĐÃ CHẾT?')")
    parser.add_argument("--subtitle", "-s", default=None, help="Dòng giải thích phụ (ví dụ: 'BÍ MẬT 90%% LÀ BOT AI')")
    parser.add_argument("--badge", "-b", default=None, help="Tag nổi bật nhỏ trên cùng (ví dụ: 'SỰ THẬT', 'BÍ ẨN')")
    parser.add_argument("--style", choices=["neon_yellow", "fire_red", "clean_white"], default="neon_yellow", help="Phong cách màu sắc")
    parser.add_argument("--time", type=float, default=2.5, help="Giây trích xuất frame từ video (mặc định: 2.5s)")
    parser.add_argument("--output", "-o", default=None, help="Đường dẫn file ảnh xuất ra")

    args = parser.parse_args()

    if args.id:
        print(f"🎨 Đang thiết kế lại ảnh bìa cho video [{args.id}]...")
        res = design_cover_for_video_id(
            video_id=args.id,
            title=args.title,
            subtitle=args.subtitle,
            badge=args.badge,
            style=args.style,
            timestamp_sec=args.time
        )
        print("=================================================================")
        print(f"✅ THIẾT KẾ ẢNH BÌA TIKTOK HOÀN TẤT!")
        print(f"🖼️ Ảnh bìa: {res['cover_top']}")
        print(f"📦 Đã đồng bộ vào: {res['cover_pkg']}")
        print("=================================================================")
    else:
        source = args.image or args.video
        out = args.output or os.path.join(COVERS_DIR, "custom_cover.jpg")
        print(f"🎨 Đang tạo ảnh bìa từ nguồn: {source}...")
        res_path = create_tiktok_cover(
            background_source=source,
            title=args.title,
            subtitle=args.subtitle,
            badge_text=args.badge,
            timestamp_sec=args.time,
            style=args.style,
            output_path=out
        )
        print("=================================================================")
        print(f"✅ ĐÃ TẠO ẢNH BÌA THÀNH CÔNG!")
        print(f"🖼️ File: {res_path}")
        print("=================================================================")

if __name__ == "__main__":
    main()
