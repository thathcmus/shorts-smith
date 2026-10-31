---
name: ai-video-producer
description: >-
  Tự động sản xuất video AI ngắn (Shorts / TikTok / Reels) chất lượng cao tại thư mục 7_Media.
  Tự động viết kịch bản giật gân theo công thức giữ chân người xem, tạo giọng đọc lồng tiếng
  truyền cảm qua Edge-TTS, áp dụng hiệu ứng chuyển động camera điện ảnh Ken Burns, Color Grading
  và Vignette qua FFmpeg, hòa âm nhạc nền MP3 điện ảnh thật và nung phụ đề động TikTok Karaoke.
---

# Kỹ năng Sản Xuất Video AI (AI Video Producer Skill V2)

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

## 2. Các điểm nâng cấp chuẩn Viral của Engine V2

1. **Phụ đề TikTok Karaoke Dynamic:**
   - Sử dụng `boundary="WordBoundary"` từ Edge-TTS để bắt nhịp từng từ.
   - Nhóm 2-4 từ ngắn, hiển thị ở 1/3 dưới màn hình (chuẩn tầm mắt).
   - Từ đang phát âm sẽ **bật sáng màu vàng Neon (`&H0000E5FF&`)**, các từ còn lại giữ màu trắng tinh khiết trên nền viền đen đậm.
2. **Nhạc nền điện ảnh thực thụ (Real Cinematic BGM):**
   - Tích hợp kho nhạc MP3 kịch tính (`assets/audio/*.mp3`), tự động lặp (loop) và né âm (audio ducking) khi có giọng nói.
3. **Hiệu ứng hình ảnh điện ảnh (Cinematic Look):**
   - Kết hợp Ken Burns với **Color Grading** (tăng contrast + saturation) và **Vignette** (tối 4 góc viền màn hình) mang phong cách phim tài liệu Hollywood.
   - Hỗ trợ cả **Video clip (.mp4)** và **Ảnh tĩnh (.jpg)**.

---

## 3. Cách sử dụng

```bash
# Chạy với kịch bản mặc định và nhạc nền điện ảnh tự động
python generate_video.py --output video_thanh_pham.mp4

# Chọn giọng đọc và bài nhạc nền riêng
python generate_video.py --voice vi-VN-NamMinhNeural --bgm assets/audio/output000.mp3 --output video_thanh_pham.mp4
```
