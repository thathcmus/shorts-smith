import json
import pytest
from unittest.mock import patch, MagicMock

from engine.script_generator import (
    generate_script_from_topic,
    get_fallback_script,
    find_script_by_index_or_path,
    derive_default_output_name,
    load_script_from_file
)

def test_fallback_script_structure():
    topic = "Kim Tự Tháp Rừng Amazon"
    script = get_fallback_script(topic, style="mystery")
    
    assert "scenes" in script
    scenes = script["scenes"]
    assert len(scenes) == 6

    for s in scenes:
        assert "role" in s
        assert "text" in s and len(s["text"]) > 10
        assert "effect" in s
        assert "prompt" in s
        # Prompts must contain cinematic styling
        prompt_lower = s["prompt"].lower()
        assert any(k in prompt_lower for k in ["cinematic", "8k", "lighting", "dramatic"])

def test_generate_script_from_topic_via_api():
    topic = "Bí Ẩn Đảo Phục Sinh"
    mock_llm_json = {
        "scenes": [
            {"role": "hook", "text": "Liệu những pho tượng Moai khổng lồ có tự biết đi?", "effect": "zoom_in_fast", "prompt": "Cinematic close-up of giant Easter Island Moai stone statue under starry night sky, dramatic lighting, 8k"},
            {"role": "fact1", "text": "Gần một nghìn bức tượng đá nguyên khối nặng đến tám mươi tấn.", "effect": "pan_down", "prompt": "Panoramic cinematic shot of green volcanic hills with monolithic Moai statues, mist, 8k"},
            {"role": "anomaly", "text": "Bộ tộc cổ xưa không có bánh xe hay cần cẩu để vận chuyển.", "effect": "zoom_in_slow", "prompt": "Ancient islanders carving gigantic stone monolith in volcanic quarry, mysterious atmosphere, 8k"},
            {"role": "theory", "text": "Nhiều nhà khảo cổ tin rằng họ sử dụng sóng âm hoặc cơ chế lắc dây.", "effect": "zoom_out", "prompt": "Walking Moai statue experiment reenactment, dramatic cinematic angle, 8k"},
            {"role": "coincidence", "text": "Tất cả các bức tượng đều quay lưng ra biển hướng về các ngôi sao.", "effect": "zoom_in_slow", "prompt": "Row of giant Moai statues facing the Milky Way galaxy, cosmic lighting, 8k"},
            {"role": "cta", "text": "Bạn tin người xưa hay nền văn minh tiên tiến đã tạo ra chúng? Hãy bình luận ngay!", "effect": "zoom_in_fast", "prompt": "Intense cinematic close-up of Moai carved stone eye with glowing cosmic reflection, 8k"}
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = json.dumps(mock_llm_json)

    with patch("requests.get", return_value=mock_resp):
        script = generate_script_from_topic(topic)
        assert len(script["scenes"]) == 6
        assert "tượng Moai" in script["scenes"][0]["text"]

def test_generate_script_fallback_on_network_failure():
    topic = "Thành Phố Atlantis Dưới Lòng Biển"
    with patch("requests.get", side_effect=Exception("Connection timed out")):
        script = generate_script_from_topic(topic)
        assert "scenes" in script
        assert len(script["scenes"]) == 6
        assert any("Atlantis" in s["text"] for s in script["scenes"])

def test_backward_compatibility_find_script():
    # Test index search
    found_001 = find_script_by_index_or_path("001")
    assert found_001 is not None
    assert "001" in found_001

    scenes = load_script_from_file(found_001)
    assert len(scenes) >= 6

    output_name = derive_default_output_name(found_001)
    assert output_name.startswith("001_video_")
