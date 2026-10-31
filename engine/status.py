"""
Hệ thống theo dõi trạng thái vòng đời video TikTok (Lifecycle & Publishing Tracker).
Quản lý 3 trạng thái rõ ràng:
  - READY: Chưa đăng / Sẵn sàng đăng
  - POSTED: Đã đăng (kèm ngày giờ, link video)
  - REJECTED: Sẽ không đăng (kèm lý do)
Tự động đồng bộ ra bảng tổng quan output/STATUS.md và cung cấp CLI tương tác.
"""
import argparse
import datetime
import glob
import json
import os
import re
from engine.config import OUTPUT_DIR

PACKAGES_DIR = os.path.join(OUTPUT_DIR, "publish_packages")
STATUS_MD_FILE = os.path.join(OUTPUT_DIR, "STATUS.md")

STATUS_ICONS = {
    "READY": "🟡 CHƯA ĐĂNG (SẴN SÀNG)",
    "POSTED": "🟢 ĐÃ ĐĂNG",
    "REJECTED": "🔴 SẼ KHÔNG ĐĂNG (HỦY)"
}

def scan_all_videos() -> list:
    """Quét tất cả các gói video trong output/publish_packages/ để lấy metadata."""
    videos = []
    if not os.path.exists(PACKAGES_DIR):
        return videos

    for pkg_name in sorted(os.listdir(PACKAGES_DIR)):
        pkg_path = os.path.join(PACKAGES_DIR, pkg_name)
        if not os.path.isdir(pkg_path):
            continue

        meta_files = glob.glob(os.path.join(pkg_path, "*metadata.json"))
        if not meta_files:
            continue

        try:
            with open(meta_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_meta_path"] = meta_files[0]
                data["_pkg_dir"] = pkg_path
                # Đảm bảo có các trường trạng thái mặc định
                if "status" not in data:
                    data["status"] = "READY"
                if "created_at" not in data:
                    data["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                if "posted_at" not in data:
                    data["posted_at"] = None
                if "post_url" not in data:
                    data["post_url"] = None
                if "note" not in data:
                    data["note"] = ""
                videos.append(data)
        except Exception:
            continue

    return videos

def update_status_dashboard(videos: list = None) -> str:
    """Tạo hoặc cập nhật tệp bảng điều khiển Markdown trực quan tại output/STATUS.md."""
    if videos is None:
        videos = scan_all_videos()

    counts = {"READY": 0, "POSTED": 0, "REJECTED": 0}
    for v in videos:
        st = v.get("status", "READY").upper()
        counts[st] = counts.get(st, 0) + 1

    lines = [
        "# 📊 BẢNG THEO DÕI TIẾN ĐỘ XUẤT BẢN VIDEO TIKTOK (PIPELINE STATUS)",
        "",
        f"> **Cập nhật lần cuối:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "### 📈 Thống kê tổng quan:",
        f"- 🟡 **Chưa đăng (Sẵn sàng):** `{counts.get('READY', 0)}` video",
        f"- 🟢 **Đã đăng thành công:** `{counts.get('POSTED', 0)}` video",
        f"- 🔴 **Sẽ không đăng (Hủy):** `{counts.get('REJECTED', 0)}` video",
        f"- 🎬 **Tổng số video:** `{len(videos)}` video",
        "",
        "---",
        "",
        "### 📋 Danh sách chi tiết các Video:",
        "",
        "| STT | Video / Chủ đề | Thời lượng | Trạng thái | Ngày tạo | Ngày đăng / Link | Ghi chú |",
        "| :---: | :--- | :---: | :---: | :---: | :--- | :--- |"
    ]

    for v in videos:
        seq = v.get("sequence", "---")
        slug = v.get("slug", "video")
        dur = f"{v.get('duration_sec', 0):.1f}s"
        st = v.get("status", "READY").upper()
        icon_label = STATUS_ICONS.get(st, st)
        created = v.get("created_at", "-")
        
        # Link hoặc ngày đăng
        post_info = "-"
        if st == "POSTED":
            url = v.get("post_url")
            posted_date = v.get("posted_at", "")
            if url:
                post_info = f"[{posted_date or 'Xem TikTok'}]({url})"
            else:
                post_info = posted_date or "Đã đăng"

        note = v.get("note", "")
        lines.append(f"| `{seq}` | **{slug}** | `{dur}` | {icon_label} | `{created}` | {post_info} | {note} |")

    lines.extend([
        "",
        "---",
        "",
        "### 🛠️ Lệnh cập nhật trạng thái nhanh qua CLI:",
        "```bash",
        "# Xem danh sách trạng thái trong Terminal",
        "python -m engine.status list",
        "",
        "# Đánh dấu đã đăng lên TikTok (kèm link video)",
        "python -m engine.status set 001 POSTED --url 'https://www.tiktok.com/@kenh/video/12345'",
        "",
        "# Đánh dấu video sẽ KHÔNG ĐĂNG (hủy / lưu trữ)",
        "python -m engine.status set 002 REJECTED --note 'Ý tưởng chưa phù hợp'",
        "",
        "# Đặt lại trạng thái sẵn sàng",
        "python -m engine.status set 001 READY",
        "```"
    ])

    content = "\n".join(lines)
    with open(STATUS_MD_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return STATUS_MD_FILE

def set_video_status(seq_or_slug: str, new_status: str, note: str = None, url: str = None) -> bool:
    """Cập nhật trạng thái của một video theo số thứ tự (ví dụ: '001') hoặc slug."""
    new_status = new_status.upper()
    if new_status not in ["READY", "POSTED", "REJECTED"]:
        raise ValueError(f"Trạng thái không hợp lệ: {new_status}. Chọn một trong: READY, POSTED, REJECTED.")

    videos = scan_all_videos()
    target = None
    for v in videos:
        if v.get("sequence") == seq_or_slug or v.get("slug") == seq_or_slug or f"{v.get('sequence')}_{v.get('slug')}" == seq_or_slug:
            target = v
            break

    if not target:
        print(f"❌ Không tìm thấy video có số thứ tự hoặc slug: '{seq_or_slug}'")
        return False

    target["status"] = new_status
    if note is not None:
        target["note"] = note
    if url is not None:
        target["post_url"] = url

    if new_status == "POSTED":
        target["posted_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    elif new_status == "READY":
        target["posted_at"] = None
        target["post_url"] = None

    # Ghi lại vào file metadata của gói
    meta_path = target["_meta_path"]
    save_data = {k: v for k, v in target.items() if not k.startswith("_")}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    # Cập nhật lại STATUS.md
    update_status_dashboard()
    print(f"✅ Đã cập nhật video [{target.get('sequence')}_{target.get('slug')}] -> {STATUS_ICONS[new_status]}")
    return True

def print_status_table():
    """In bảng trạng thái ra console cực kỳ rõ ràng, dễ nhìn."""
    videos = scan_all_videos()
    print("\n=========================================================================================")
    print("📊 TỔNG QUAN TRẠNG THÁI XUẤT BẢN VIDEO TIKTOK (PIPELINE STATUS)")
    print("=========================================================================================")
    print(f"{'STT':<6} | {'Tên Video / Slug':<25} | {'Thời lượng':<10} | {'Trạng thái':<22} | Ghi chú / Link")
    print("-" * 89)
    if not videos:
        print("  (Chưa có video nào trong output/publish_packages/)")
    else:
        for v in videos:
            seq = v.get("sequence", "---")
            slug = v.get("slug", "video")[:23]
            dur = f"{v.get('duration_sec', 0):.1f}s"
            st = v.get("status", "READY").upper()
            icon_label = STATUS_ICONS.get(st, st)
            note = v.get("note", "")
            if v.get("post_url"):
                note = f"{v['post_url']} ({note})" if note else v['post_url']
            print(f"{seq:<6} | {slug:<25} | {dur:<10} | {icon_label:<22} | {note}")
    print("=" * 89)
    print(f"👉 Xem bảng chi tiết đẹp mắt tại: output/STATUS.md\n")

def main():
    parser = argparse.ArgumentParser(description="Quản lý trạng thái xuất bản Video TikTok")
    subparsers = parser.add_subparsers(dest="command")

    # Command list
    subparsers.add_parser("list", help="Xem danh sách trạng thái tất cả video")

    # Command set
    set_parser = subparsers.add_parser("set", help="Cập nhật trạng thái cho video")
    set_parser.add_argument("id", help="Số thứ tự (ví dụ: 001) hoặc tên slug của video")
    set_parser.add_argument("status", choices=["READY", "POSTED", "REJECTED", "ready", "posted", "rejected"], help="Trạng thái mới")
    set_parser.add_argument("--note", "-n", default=None, help="Ghi chú (lý do hủy, giờ đăng...)")
    set_parser.add_argument("--url", "-u", default=None, help="Đường link video TikTok sau khi đăng")

    args = parser.parse_args()

    if args.command == "set":
        set_video_status(args.id, args.status, note=args.note, url=args.url)
    else:
        print_status_table()

if __name__ == "__main__":
    main()
