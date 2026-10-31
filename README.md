# AI Media & Video Maker

Công cụ tự động hóa sản xuất video ngắn (Shorts / Reels / Drama) sử dụng AI voiceover, hiệu ứng chuyển động hình ảnh và âm thanh nền kịch tính.

## Tính năng chính
- Tự động tạo giọng đọc thuyết minh tiếng Việt với `edge-tts`.
- Tự động tổng hợp nhạc nền Tension/Suspense (Sub-bass, Heartbeat, hiệu ứng âm thanh vũ trụ).
- Hiệu ứng chuyển động điện ảnh (Zoom in, Pan, Zoom out) cho từng cảnh hình ảnh qua `ffmpeg`.
- Tự động tạo và nung phụ đề viền vàng nổi bật dạng `.ass`.
- Ghép nối và xuất video định dạng dọc (1080x1920) chuẩn Shorts / TikTok.

## Cài đặt thư viện phụ thuộc
```bash
pip install edge-tts imageio-ffmpeg numpy
```

## Cách chạy
```bash
python ai_video_maker.py
```
