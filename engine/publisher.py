"""
Mô-đun đóng gói xuất bản TikTok (TikTok Publisher & Caption Workspace).
Tự động đánh số thứ tự (001_, 002_...), tạo caption tối ưu SEO TikTok,
trích xuất ảnh bìa Thumbnail và đóng gói đồng bộ giữa video và caption.
"""
import glob
import json
import os
import re
import shutil
import subprocess
from engine.config import FFMPEG_EXE, BASE_DIR, OUTPUT_DIR

CAP_DIR = os.path.join(OUTPUT_DIR, "cap")
COVERS_DIR = os.path.join(OUTPUT_DIR, "covers")
PACKAGES_DIR = os.path.join(OUTPUT_DIR, "publish_packages")

os.makedirs(CAP_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(PACKAGES_DIR, exist_ok=True)

def get_next_sequence_prefix(output_dir: str = OUTPUT_DIR) -> str:
    """
    Quét output/, output/cap/, output/covers/ và output/publish_packages/ để tìm số thứ tự lớn nhất.
    Trả về chuỗi số thứ tự kế tiếp dạng 3 chữ số: '001', '002', '003'...
    """
    prefixes = []
    scan_dirs = [
        output_dir,
        os.path.join(output_dir, "cap"),
        os.path.join(output_dir, "covers"),
        os.path.join(output_dir, "publish_packages")
    ]
    for d in scan_dirs:
        if os.path.exists(d):
            for entry in os.listdir(d):
                m = re.match(r"^(\d{2,4})_", entry)
                if m:
                    prefixes.append(int(m.group(1)))
    next_num = max(prefixes) + 1 if prefixes else 1
    return f"{next_num:03d}"

def parse_sequence_and_slug(name_or_slug: str, output_dir: str = OUTPUT_DIR) -> tuple[str, str]:
    """
    Phân tích tiền tố số thứ tự và slug sạch.
    Nếu chưa có tiền tố số (001_), tự động cấp phát số thứ tự tiếp theo.
    """
    base = os.path.splitext(os.path.basename(name_or_slug))[0]
    
    # Kiểm tra xem có tiền tố số chưa
    m = re.match(r"^(\d{2,4})_(.*)$", base)
    if m:
        seq = m.group(1)
        raw_slug = m.group(2)
    else:
        seq = get_next_sequence_prefix(output_dir)
        raw_slug = base

    # Làm sạch slug bỏ chữ video_ nếu có ở đầu
    clean_slug = re.sub(r"^video_", "", raw_slug)
    if not clean_slug:
        clean_slug = "tiktok_video"

    return seq, clean_slug

def generate_tiktok_caption(scenes: list, title: str = None) -> str:
    """
    Tự động viết Caption TikTok chuẩn công thức Viral:
    [HOOK GIẬT GÂN] + [NỘI DUNG TÓM TẮT] + [CALL TO ACTION GÂY TRANH CÃI] + [BỘ HASHTAG ĐỀ XUẤT]
    """
    hook_text = scenes[0]["text"] if scenes else ""
    cta_text = scenes[-1]["text"] if len(scenes) > 1 else ""

    if not title:
        title = hook_text.split("...")[0].replace("?", "").strip()
        if len(title) > 60:
            title = title[:60] + "..."

    all_text = " ".join([s.get("text", "") for s in scenes]).lower()
    if "atlantis" in all_text or "sahara" in all_text or "richat" in all_text:
        hashtags = "#atlantis #matsahara #richatstructure #bian #khoahoc #kienthuc #thuyetammuu #lichsu #learnontiktok #fyp #xuhuong #viral"
    elif "kim tự tháp" in all_text or "ai cập" in all_text or "pyramid" in all_text:
        hashtags = "#kimtuthap #aicap #pyramid #kienthuc #bian #thuyetammuu #khoahoc #lichsu #learnontiktok #fyp #xuhuong #viral"
    elif "internet" in all_text or "bot" in all_text or "ai" in all_text:
        hashtags = "#deadinternettheory #thuyetammuu #bian #kienthuc #congnghe #trietly #learnontiktok #fyp #xuhuong #viral"
    else:
        hashtags = "#bian #kienthuc #khoahoc #thuyetammuu #khampha #bianthegioi #learnontiktok #fyp #xuhuong #viral"

    caption_lines = [
        f"🚨 {title.upper()} 🚨",
        "",
        f"👉 {hook_text}",
        "",
        "Bạn nghĩ đây là sự thật hay chỉ là một giả thuyết điên rồ?",
        f"💬 {cta_text}",
        "",
        "---",
        "📌 Hashtags tối ưu thuật toán:",
        hashtags
    ]
    return "\n".join(caption_lines)

def extract_thumbnail_from_video(video_path: str, thumbnail_path: str, timestamp_sec: float = 2.5) -> str:
    """Trích xuất 1 frame ảnh bìa chất lượng cao tại thời điểm đắt giá của video."""
    os.makedirs(os.path.dirname(os.path.abspath(thumbnail_path)), exist_ok=True)
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", str(timestamp_sec),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        thumbnail_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return thumbnail_path

def create_publish_workspace(
    video_path: str,
    scenes: list,
    slug: str = None,
    duration: float = None
) -> dict:
    """
    Đóng gói toàn diện sản phẩm vào không gian xuất bản với tiền tố số thứ tự đồng bộ:
    1. output/cap/{seq}_cap_{slug}.txt (Dễ dàng tra cứu 1:1 với video)
    2. output/publish_packages/{seq}_{slug}/:
       - {seq}_video_{slug}.mp4
       - {seq}_cap_{slug}.txt
       - {seq}_cover_{slug}.jpg
       - {seq}_metadata.json
    3. Đảm bảo file video trong output/ cũng có tiền tố {seq}_ để trace chuẩn xác.
    """
    seq, clean_slug = parse_sequence_and_slug(slug or os.path.basename(video_path))
    
    # Tên chuẩn hóa đồng bộ 100% giữa video và caption
    video_filename = f"{seq}_video_{clean_slug}.mp4"
    cap_filename = f"{seq}_cap_{clean_slug}.txt"
    thumb_filename = f"{seq}_cover_{clean_slug}.jpg"
    meta_filename = f"{seq}_metadata.json"
    package_dir_name = f"{seq}_{clean_slug}"

    # 1. Viết Caption chuẩn TikTok
    caption_content = generate_tiktok_caption(scenes)

    # 2. Lưu vào output/cap/{seq}_cap_{slug}.txt
    cap_file_path = os.path.join(CAP_DIR, cap_filename)
    with open(cap_file_path, "w", encoding="utf-8") as f:
        f.write(caption_content)

    # 3. Tạo thư mục trọn gói output/publish_packages/{seq}_{slug}/
    pkg_dir = os.path.join(PACKAGES_DIR, package_dir_name)
    os.makedirs(pkg_dir, exist_ok=True)

    pkg_caption_path = os.path.join(pkg_dir, cap_filename)
    with open(pkg_caption_path, "w", encoding="utf-8") as f:
        f.write(caption_content)

    # Trích xuất Thumbnail ảnh bìa vào output/covers/ và đồng bộ vào publish_packages/
    top_cover_path = os.path.join(COVERS_DIR, thumb_filename)
    pkg_thumb_path = os.path.join(pkg_dir, thumb_filename)

    # Ưu tiên lấy ảnh gốc sạch từ cảnh đầu tiên (để KHÔNG BAO GIỜ bị dính chữ phụ đề nung trên video)
    clean_scene_img = None
    if scenes:
        for sc in scenes:
            cand = sc.get("image") or sc.get("media")
            if cand:
                full_p = os.path.join(BASE_DIR, cand) if not os.path.isabs(cand) else cand
                if os.path.exists(full_p) and not full_p.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
                    clean_scene_img = full_p
                    break

    if clean_scene_img:
        # Dùng ảnh gốc sạch làm nền cho ảnh bìa
        from engine.cover_designer import create_tiktok_cover
        create_tiktok_cover(
            background_source=clean_scene_img,
            title=clean_slug.upper().replace("_", " "),
            subtitle=None,
            badge_text="BÍ ẨN",
            output_path=top_cover_path
        )
    else:
        extract_thumbnail_from_video(video_path, top_cover_path, timestamp_sec=0.1)

    if os.path.exists(top_cover_path):
        shutil.copy2(top_cover_path, pkg_thumb_path)

    # Đồng bộ file video trong thư mục package
    pkg_video_path = os.path.join(pkg_dir, video_filename)
    if os.path.abspath(video_path) != os.path.abspath(pkg_video_path):
        shutil.copy2(video_path, pkg_video_path)

    # Đảm bảo video trong output/ cũng có bản sao hoặc đổi tên đúng tiền tố {seq}_
    out_video_with_seq = os.path.join(OUTPUT_DIR, video_filename)
    if os.path.abspath(video_path) != os.path.abspath(out_video_with_seq):
        shutil.copy2(video_path, out_video_with_seq)

    import datetime
    # Lưu metadata.json
    metadata = {
        "sequence": seq,
        "slug": clean_slug,
        "video_file": video_filename,
        "caption_file": cap_filename,
        "duration_sec": duration,
        "scenes_count": len(scenes),
        "package_dir": f"output/publish_packages/{package_dir_name}",
        "status": "READY",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "posted_at": None,
        "post_url": None,
        "note": "Sẵn sàng đăng"
    }
    pkg_meta_path = os.path.join(pkg_dir, meta_filename)
    with open(pkg_meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Tự động cập nhật bảng điều khiển Markdown output/STATUS.md
    try:
        from engine.status import update_status_dashboard
        update_status_dashboard()
    except Exception:
        pass

    return {
        "seq": seq,
        "clean_slug": clean_slug,
        "video_file": out_video_with_seq,
        "cap_file": cap_file_path,
        "cover_file": top_cover_path,
        "package_dir": pkg_dir,
        "thumbnail": top_cover_path,
        "caption_text": caption_content
    }
