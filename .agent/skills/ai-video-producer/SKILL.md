---
name: ai-video-producer
description: >-
  Tự động sản xuất video AI ngắn (Shorts / TikTok / Reels) chất lượng cao tại thư mục 7_Media.
  Tự động viết kịch bản giật gân theo công thức giữ chân người xem, tạo giọng đọc lồng tiếng
  truyền cảm qua Edge-TTS, áp dụng hiệu ứng chuyển động camera điện ảnh Ken Burns qua FFmpeg,
  hòa âm nhạc nền Tension và nung phụ đề vàng hổ phách nổi bật.
---

# Kỹ năng Sản Xuất Video AI (AI Video Producer Skill)

Skill này cung cấp quy trình khép kín giúp AI Agent và lập trình viên tạo ra các video ngắn đạt chuẩn điện ảnh và mức độ tương tác cao (Viral Shorts/Reels/TikTok) ngay trong thư mục `7_Media`.

---

## 1. Cấu trúc kịch bản 6 cảnh chuẩn giữ chân người xem (~60 Giây)

Khi người dùng yêu cầu: *"Làm video về [Chủ đề]"*, hãy xây dựng kịch bản chia làm 6 cảnh theo đúng nhịp điệu tâm lý sau:

1. **Cảnh 1 - The 3s Hook (Giật gân mở màn):**
   - Đặt câu hỏi gây sốc hoặc phủ định niềm tin thông thường để người xem không lướt qua.
   - *Hiệu ứng camera khuyến nghị:* `zoom_in_fast`.
2. **Cảnh 2 - The Scale / Facts (Quy mô khổng lồ):**
   - Đưa ra các con số, kích thước hoặc mốc thời gian gây choáng ngợp.
   - *Hiệu ứng camera khuyến nghị:* `pan_down`.
3. **Cảnh 3 - The Anomaly (Nghịch lý / Bí ẩn):**
   - Điểm dị thường mà khoa học hoặc lịch sử chính thống chưa giải thích được.
   - *Hiệu ứng camera khuyến nghị:* `zoom_in_slow`.
4. **Cảnh 4 - The Shock Theory (Giả thuyết chấn động):**
   - Giả thuyết về nền văn minh tiền sử, công nghệ ngoài hành tinh hoặc dự án bí mật.
   - *Hiệu ứng camera khuyến nghị:* `zoom_out`.
5. **Cảnh 5 - The Cosmic Alignment (Trùng hợp kỳ lạ):**
   - Sự trùng hợp rợn người với tọa độ, thiên văn học hoặc toán học vũ trụ.
   - *Hiệu ứng camera khuyến nghị:* `zoom_in_slow`.
6. **Cảnh 6 - The Cliffhanger & Call-to-Action (Kêu gọi tranh luận):**
   - Câu hỏi mở để người xem để lại bình luận và tranh cãi.
   - *Hiệu ứng camera khuyến nghị:* `zoom_in_fast`.

---

## 2. Quy trình thực hiện tự động

### Bước A: Tạo kịch bản JSON
Lưu kịch bản vào tệp JSON (ví dụ: `script_topic.json`):
```json
{
  "scenes": [
    {
      "image": "scene1.jpg",
      "text": "Câu thoại cảnh 1...",
      "effect": "zoom_in_fast"
    },
    ...
  ]
}
```

### Bước B: Chuẩn bị hình ảnh
- Đảm bảo mỗi cảnh có 1 hình ảnh tương ứng (`scene1.jpg`, `scene2.jpg`, v.v.).
- Nếu thiếu ảnh, có thể yêu cầu subagent `image-generator` vẽ ảnh điện ảnh chân thật theo prompt mô tả cảnh.

### Bước C: Chạy lệnh sản xuất video
Chạy CLI engine tích hợp:
```bash
python generate_video.py --script script_topic.json --output video_thanh_pham.mp4 --aspect vertical
```

---

## 3. Các tham số cấu hình nhanh

* `--voice`:
  - `vi-VN-NamMinhNeural` (Mặc định: Nam đanh thép, bí ẩn, tài liệu)
  - `vi-VN-HoaiMyNeural` (Nữ truyền cảm, ấm áp)
  - `en-US-ChristopherNeural` (Nam tiếng Anh tài liệu)
  - `en-US-JennyNeural` (Nữ tiếng Anh tự nhiên)
* `--aspect`:
  - `vertical`: 1080x1920 (9:16 chuẩn TikTok / Shorts)
  - `horizontal`: 1920x1080 (16:9 chuẩn YouTube)
* `--bgm-volume`: Mặc định `0.22` (Audio ducking tự động để không lấn át giọng thuyết minh).
