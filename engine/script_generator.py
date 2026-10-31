"""
Module quản lý kịch bản: cấu trúc 6 cảnh chuẩn shorts viral (~60 giây).
"""
import json
import os

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
