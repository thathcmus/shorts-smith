# AI Media & Video Producer

Hệ thống sản xuất video AI ngắn (Shorts / Reels / TikTok) tự động, chất lượng điện ảnh tại thư mục `7_Media`. Được xây dựng theo mô hình tối ưu từ kiến trúc của MoneyPrinterTurbo nhưng tinh gọn, chạy trực tiếp không cần cài đặt cồng kềnh.

## ✨ Điểm nổi bật
- **Antigravity Skill Tích hợp:** AI Assistant tự động nhận lệnh chat (VD: *"Tạo video 60s chủ đề Kim Tự Tháp"*) để viết kịch bản và chạy render.
- **Giọng đọc Edge-TTS:** Lồng tiếng tự nhiên không tốn phí, đa dạng giọng Nam/Nữ tiếng Việt và tiếng Anh.
- **Chuyển động điện ảnh Ken Burns:** Filter FFmpeg tạo chuyển động camera mượt mà (Zoom in, Pan down, Zoom out) thay vì ảnh tĩnh.
- **Audio Ducking:** Nhạc nền Tension/Suspense tự động hạ âm lượng vừa vặn tôn giọng đọc.
- **Phụ đề Amber Gold:** Viền đen, bóng mờ, vàng hổ phách nổi bật chuẩn phong cách video viral.

## 📁 Cấu trúc thư mục
```
7_Media/
├── .agent/skills/ai-video-producer/  # Skill chuẩn cho AI Assistant
├── engine/                          # Bộ thư viện xử lý cốt lõi
│   ├── config.py                    # Cấu hình độ phân giải, FPS, giọng đọc
│   ├── effects.py                   # Bộ lọc FFmpeg Ken Burns
│   ├── render.py                    # Ghép video, hòa âm BGM và nung phụ đề
│   ├── script_generator.py          # Quản lý cấu trúc kịch bản 6 cảnh
│   └── tts.py                       # Tổng hợp giọng đọc và định dạng phụ đề ASS
├── generate_video.py                # Điểm vào CLI chính
└── output/                          # Thư mục chứa video thành phẩm
```

## 🚀 Cách sử dụng

### Cách 1: Ra lệnh trực tiếp cho AI trong chat
Bạn chỉ cần nhắn trong khung chat:
> *"Tạo video ngắn 60s về chủ đề [Chủ đề mong muốn]"*

AI sẽ tự động đọc Skill, tạo kịch bản 6 cảnh, ghép nối ảnh và xuất video ra thư mục `output/`.

### Cách 2: Sử dụng dòng lệnh (CLI)
```bash
# Chạy với kịch bản có sẵn
python generate_video.py

# Xuất video với tên tùy chỉnh và giọng đọc nữ
python generate_video.py --output video_moi.mp4 --voice vi-VN-HoaiMyNeural

# Chạy với tệp kịch bản JSON riêng
python generate_video.py --script my_script.json --aspect vertical
```
