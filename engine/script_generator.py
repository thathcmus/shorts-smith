"""
Module quản lý kịch bản: cấu trúc 6 cảnh chuẩn shorts viral (~60 giây).
Hỗ trợ tìm kịch bản theo index (001, 3, 4...), theo slug hoặc theo đường dẫn file.
"""
import glob
import json
import os
import re

TEMPLATES = {
    "mystery": [
        {"role": "hook", "desc": "Câu hỏi gây sốc, phủ định niềm tin thông thường trong 3 giây đầu", "effect": "zoom_in_fast"},
        {"role": "fact1", "desc": "Đưa ra các con số hoặc kích thước khổng lồ khó lý giải", "effect": "pan_down"},
        {"role": "anomaly", "desc": "Điểm nghịch lý kỳ lạ nhất mà giới khoa học bối rối", "effect": "zoom_in_slow"},
        {"role": "theory", "desc": "Giả thuyết chấn động: công nghệ cổ đại hoặc nền văn minh tiền sử", "effect": "zoom_out"},
        {"role": "coincidence", "desc": "Sự trùng hợp rùng mình liên quan đến toán học hoặc vũ trụ", "effect": "zoom_in_slow"},
        {"role": "cta", "desc": "Câu hỏi mở kích thích tranh luận và bình luận", "effect": "zoom_in_fast"}
    ]
}

def load_script_from_file(json_path: str) -> list:
    """Tải kịch bản từ tệp JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "scenes" in data:
        return data["scenes"]
    return data

def save_script_to_file(scenes: list, output_json: str):
    """Lưu kịch bản ra tệp JSON."""
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"scenes": scenes}, f, ensure_ascii=False, indent=2)

def find_script_by_index_or_path(script_target: str, examples_dir: str = "examples") -> str:
    """
    Tìm đường dẫn file JSON kịch bản dựa vào:
    1. Số index (ví dụ: '003', '3', '001', '1', '4'...)
    2. Slug hoặc từ khóa (ví dụ: 'gunung_padang', 'derinkuyu', 'baalbek')
    3. Đường dẫn trực tiếp (ví dụ: 'examples/003_script_gunung_padang.json')
    """
    if not script_target:
        default_script = os.path.join(examples_dir, "script_pyramid_example.json")
        if os.path.exists(default_script):
            return default_script
        return None

    # 1. Nếu là đường dẫn file có sẵn trực tiếp
    if os.path.isfile(script_target):
        return script_target

    # 2. Nếu nằm trong examples_dir với tên đầy đủ
    in_examples = os.path.join(examples_dir, script_target)
    if os.path.isfile(in_examples):
        return in_examples
    if not script_target.endswith(".json") and os.path.isfile(f"{in_examples}.json"):
        return f"{in_examples}.json"

    # Lấy danh sách tất cả các file JSON trong examples/
    if os.path.exists(examples_dir):
        all_json_files = glob.glob(os.path.join(examples_dir, "*.json"))
    else:
        all_json_files = []

    # 3. Tìm theo index dạng số (ví dụ: '3' -> '003', '03' -> '003', '003')
    num_match = re.match(r"^(\d{1,4})$", script_target.strip())
    if num_match:
        idx_num = int(num_match.group(1))
        # Tìm các file bắt đầu bằng số thứ tự này (ví dụ: 003_ hoặc 3_)
        for f in all_json_files:
            fname = os.path.basename(f)
            m = re.match(r"^(\d{1,4})_", fname)
            if m and int(m.group(1)) == idx_num:
                return f

    # 4. Tìm theo từ khóa / slug trong tên file (ví dụ: 'gunung_padang', 'baalbek')
    target_clean = script_target.strip().lower()
    matches = []
    for f in all_json_files:
        fname = os.path.basename(f).lower()
        if target_clean in fname:
            matches.append(f)

    if matches:
        return matches[0]

    # Nếu không tìm thấy, liệt kê các kịch bản có sẵn để gợi ý cho người dùng
    available = [os.path.basename(f) for f in all_json_files]
    avail_str = "\n".join([f"   - {item}" for item in available]) if available else "   (Chưa có kịch bản nào)"
    raise FileNotFoundError(
        f"❌ Không tìm thấy kịch bản nào khớp với index hoặc đường dẫn: '{script_target}'\n"
        f"📋 Danh sách các kịch bản khả dụng trong '{examples_dir}':\n{avail_str}"
    )

def derive_default_output_name(script_path: str) -> str:
    """
    Tự động suy luận tên file output MP4 từ tên file kịch bản.
    Ví dụ: 'examples/003_script_gunung_padang.json' -> '003_video_gunung_padang.mp4'
           '001_script_dead_internet.json' -> '001_video_dead_internet.mp4'
    """
    if not script_path:
        return None
    base = os.path.splitext(os.path.basename(script_path))[0]
    # Mẫu 1: 003_script_gunung_padang -> 003_video_gunung_padang.mp4
    m = re.match(r"^(\d{2,4})_script_(.*)$", base)
    if m:
        return f"{m.group(1)}_video_{m.group(2)}.mp4"
    # Mẫu 2: 003_gunung_padang -> 003_video_gunung_padang.mp4
    m = re.match(r"^(\d{2,4})_(.*)$", base)
    if m:
        clean = re.sub(r"^script_", "", m.group(2))
        return f"{m.group(1)}_video_{clean}.mp4"
    # Mẫu 3: script_dead_internet -> video_dead_internet.mp4
    clean = re.sub(r"^script_", "", base)
    return f"video_{clean}.mp4"
