"""
Module quản lý và tự động sinh kịch bản: cấu trúc 6 cảnh chuẩn shorts viral (~40-60 giây).
Hỗ trợ:
- Tự động sinh kịch bản từ chủ đề bất kỳ (LLM đám mây miễn phí + Offline Fallback)
- Tìm kịch bản theo index (001, 3, 4...), theo slug hoặc theo đường dẫn file.
"""
import glob
import json
import os
import re
import urllib.parse
import requests

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

def get_fallback_script(topic: str, style: str = "mystery") -> dict:
    """
    Tạo kịch bản dự phòng 6 cảnh chuẩn tâm lý giật gân khi không có kết nối mạng.
    Bao gồm câu thoại tiếng Việt truyền cảm và visual prompt tiếng Anh chuẩn điện ảnh 8k.
    """
    clean_topic = topic.strip()
    return {
        "title": clean_topic,
        "scenes": [
            {
                "role": "hook",
                "text": f"Bạn có tin rằng bí mật lớn nhất về {clean_topic}... thực chất đã bị che giấu suốt hàng nghìn năm?",
                "effect": "zoom_in_fast",
                "prompt": f"Cinematic dramatic close-up revealing ancient mysterious artifact representing {clean_topic}, eerie volumetric lighting, dark moody atmosphere, 8k"
            },
            {
                "role": "fact1",
                "text": f"Các nhà nghiên cứu phát hiện cấu trúc phi thường của {clean_topic} vượt xa mọi quy chuẩn kỹ thuật của thời đại đó!",
                "effect": "pan_down",
                "prompt": f"Panoramic cinematic establishing shot of monumental ancient ruins of {clean_topic}, epic scale, mystical morning fog, 8k"
            },
            {
                "role": "anomaly",
                "text": "Điểm kỳ lạ nhất là: không hề có bất kỳ dấu vết công cụ hay tài liệu nào ghi chép lại cách nó được tạo ra.",
                "effect": "zoom_in_slow",
                "prompt": f"Intricate high-detail carvings and anomalous monolithic architecture of {clean_topic}, mysterious glowing symbols, dramatic cinematic shadows, 8k"
            },
            {
                "role": "theory",
                "text": f"Nhiều giả thuyết chấn động cho rằng {clean_topic} là di sản của một nền văn minh tiền sử sở hữu công nghệ đã bị lãng quên.",
                "effect": "zoom_out",
                "prompt": f"Breathtaking wide view of advanced ancient civilization around {clean_topic}, futuristic architectural elements, golden hour cinematic lighting, 8k"
            },
            {
                "role": "coincidence",
                "text": "Thậm chí kinh ngạc hơn: vị trí tọa độ của nó lại thẳng hàng hoàn hảo với các chòm sao trên bầu trời vũ trụ!",
                "effect": "zoom_in_slow",
                "prompt": f"Ancient astronomical alignment of {clean_topic} pointing directly toward the glowing Milky Way galaxy, cosmic dramatic night sky, 8k"
            },
            {
                "role": "cta",
                "text": f"Theo bạn, {clean_topic} là sự trùng hợp hay bằng chứng có thật? Hãy để lại bình luận góc nhìn của bạn ngay!",
                "effect": "zoom_in_fast",
                "prompt": f"Mysterious glowing ancient portal eye carved in stone representing the legacy of {clean_topic}, hyper-detailed cinematic concept art, 8k"
            }
        ]
    }

def is_script_vietnamese_fluent(scenes: list) -> bool:
    """
    Kiểm tra tính tự nhiên và ngữ nghĩa của câu thoại tiếng Việt:
    - Loại bỏ các kịch bản chứa từ ngô nghê/ảo giác ("vô vẩn", "tứ quẩn", "thổi chiều", "khai hình", "hòm sao", "thật cấu", "thiên dương", "băng kẽ").
    - Đảm bảo độ dài trung bình của từ hợp lý và tỷ lệ ký tự có dấu thanh tiếng Việt đạt chuẩn.
    """
    garbled_keywords = [
        "vô vẩn", "tứ quẩn", "thổi chiều", "khai hình", "hòm sao",
        "thật cấu", "thiên dương", "băng kẽ", "đồng thời hiện tượng băng",
        "chục cổ trong"
    ]
    full_text = " ".join(s.get("text", "") for s in scenes).lower()
    for bad in garbled_keywords:
        if bad in full_text:
            return False

    # Kiểm tra tỷ lệ ký tự tiếng Việt có dấu
    vn_marks = re.findall(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", full_text)
    words = full_text.split()
    if not words or len(vn_marks) / max(len(words), 1) < 0.3:
        return False

    return True

def generate_script_from_topic(topic: str, style: str = "mystery") -> dict:
    """
    Tự động sinh kịch bản 6 cảnh từ chủ đề gợi ý qua dịch vụ AI văn bản miễn phí.
    Tự động chuyển sang chế độ fallback an toàn nếu gặp sự cố kết nối mạng.
    """
    clean_topic = (topic or "").strip() or "Bí Ẩn Thế Giới"
    system_instruction = (
        "Bạn là một biên kịch video ngắn TikTok/Shorts tài liệu bí ẩn triệu view. "
        f"Hãy viết một kịch bản 6 phân cảnh bằng tiếng Việt về chủ đề: '{clean_topic}'. "
        "Yêu cầu định dạng JSON CHÍNH XÁC có key 'scenes' chứa 6 object: "
        "mỗi object có 'role' (hook, fact1, anomaly, theory, coincidence, cta), "
        "'text' (câu thoại tiếng Việt dồn dập, giật gân, nhịp 1.5x), "
        "'effect' (chọn một trong: zoom_in_fast, pan_down, zoom_in_slow, zoom_out), "
        "'prompt' (mô tả visual prompt tiếng Anh cực kỳ chi tiết cho AI vẽ ảnh: Cinematic, 8k, dramatic lighting, vertical composition). "
        "Chỉ trả về JSON thuần túy, không có giải thích thêm."
    )
    
    encoded_prompt = urllib.parse.quote(system_instruction)
    api_url = f"https://text.pollinations.ai/{encoded_prompt}?json=true&model=openai"

    try:
        resp = requests.get(api_url, timeout=12)
        if resp.status_code == 200:
            raw_text = resp.text.strip()
            # Làm sạch markdown ```json nếu có
            if "```" in raw_text:
                m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
                if m:
                    raw_text = m.group(1).strip()
            
            data = json.loads(raw_text)
            if (
                isinstance(data, dict)
                and "scenes" in data
                and len(data["scenes"]) == 6
                and all(isinstance(s, dict) and s.get("text") and s.get("prompt") for s in data["scenes"])
                and is_script_vietnamese_fluent(data["scenes"])
            ):
                return data
    except Exception:
        pass

    # Nếu không kết nối được hoặc JSON lỗi, dùng bộ fallback thông minh
    return get_fallback_script(clean_topic, style=style)

def load_script_from_file(json_path: str) -> list:
    """Tải kịch bản từ tệp JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "scenes" in data:
        return data["scenes"]
    return data

def save_script_to_file(scenes: list, output_json: str):
    """Lưu kịch bản ra tệp JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
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
    m = re.match(r"^(\d{2,4})_script_(.*)$", base)
    if m:
        return f"{m.group(1)}_video_{m.group(2)}.mp4"
    m = re.match(r"^(\d{2,4})_(.*)$", base)
    if m:
        clean = re.sub(r"^script_", "", m.group(2))
        return f"{m.group(1)}_video_{clean}.mp4"
    clean = re.sub(r"^script_", "", base)
    return f"video_{clean}.mp4"
