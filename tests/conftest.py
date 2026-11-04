import io
import os
import shutil
import tempfile
import pytest
from PIL import Image

@pytest.fixture
def sample_scene_payload():
    return [
        {
            "role": "hook",
            "text": "Bạn có nhận ra thế giới mạng ngày càng trở nên vô hồn không?",
            "effect": "zoom_in_fast",
            "prompt": "Cinematic close-up of human eyes reflecting digital code, dark cyberpunk room, 8k, dramatic lighting"
        },
        {
            "role": "fact1",
            "text": "Hơn sáu mươi phần trăm nội dung trực tuyến hiện nay được điều khiển bởi bot tự động.",
            "effect": "pan_down",
            "prompt": "Endless high-tech server racks with pulsing blue data streams, futuristic cyberspace, cinematic 8k"
        },
        {
            "role": "anomaly",
            "text": "Những cuộc tranh luận nảy lửa thực chất chỉ là kịch bản được lập trình sẵn.",
            "effect": "zoom_in_slow",
            "prompt": "A solitary human silhouette in dark room surrounded by ghostly holographic avatars, moody atmosphere"
        },
        {
            "role": "theory",
            "text": "Giả thuyết khẳng định Internet nguyên bản của con người đã kết thúc từ nhiều năm trước.",
            "effect": "zoom_out",
            "prompt": "A giant digital simulation dome over a neon metropolis, surreal cyberpunk concept art, cinematic"
        },
        {
            "role": "coincidence",
            "text": "Sự trùng hợp là bạn đang xem video này vào đúng khoảnh khắc thuật toán đã tính toán trước.",
            "effect": "zoom_in_slow",
            "prompt": "Glowing cyber hourglass with binary numbers falling like sand in deep dark space, volumetric light"
        },
        {
            "role": "cta",
            "text": "Bình luận 'TÔI' ngay bây giờ để xác nhận bạn thực sự là một con người bằng xương bằng thịt!",
            "effect": "zoom_in_fast",
            "prompt": "Biometric fingerprint scanner interface with HUD text saying HUMAN VERIFICATION REQUIRED, neon green"
        }
    ]

@pytest.fixture
def mock_image_bytes():
    """Generates valid 1080x1920 JPEG image bytes using Pillow."""
    img = Image.new("RGB", (1080, 1920), color=(30, 40, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

@pytest.fixture
def temp_test_dir():
    """Creates a temporary workspace directory and deletes it afterwards."""
    path = tempfile.mkdtemp(prefix="7_media_test_")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
