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

4. **Tốc độ đọc 1.5x dồn dập chuẩn TikTok:**
   - Cấu hình mặc định toàn hệ thống là `DEFAULT_SPEECH_RATE = "+50%"` trong `engine/config.py`, bắt nhịp nhanh, dứt khoát và tối ưu giữ chân người xem.
5. **Không gian xuất bản trọn gói đánh số thứ tự đồng bộ (Sequential Publishing & Caption Workspace):**
   - Hệ thống tự động phát hiện và cấp phát số thứ tự 3 chữ số (`001_`, `002_`, `003_`...) để **đối chiếu 1:1 tuyệt đối giữa Video và Caption**:
     - `output/{seq}_video_{slug}.mp4`: Video thành phẩm có tiền tố số thứ tự.
     - `output/cap/{seq}_cap_{slug}.txt`: File Caption TikTok chuẩn SEO (Tiêu đề in hoa, Hook, Kêu gọi bình luận CTA, và dàn Hashtags hot) mang cùng tiền tố `{seq}_` để mở copy ngay.
     - `output/publish_packages/{seq}_{slug}/`: Gói xuất bản độc lập chứa trọn bộ `{seq}_video_{slug}.mp4`, `{seq}_cap_{slug}.txt`, `{seq}_cover_{slug}.jpg` (ảnh bìa thumbnail 1080x1920) và `{seq}_metadata.json`.
6. **Theo dõi trạng thái vòng đời xuất bản (Publishing Status Tracker):**
   - Quản lý 3 trạng thái rõ ràng của từng video:
     - 🟡 `READY`: Video đã dựng xong, chưa đăng (sẵn sàng đăng).
     - 🟢 `POSTED`: Đã đăng lên kênh TikTok (kèm ngày giờ, link video thực tế).
     - 🔴 `REJECTED`: Sẽ không đăng (bị hủy hoặc lưu trữ nội bộ, kèm lý do).
   - Tự động đồng bộ ra bảng điều khiển trực quan tại `output/STATUS.md` và tra cứu/cập nhật nhanh qua CLI `python -m engine.status`.
7. **Tổ chức hình ảnh theo từng thư mục video:**
   - Toàn bộ ảnh tĩnh/footage phục vụ cho từng video được lưu độc lập tại `sample_assets/{seq}_{slug}/` (ví dụ: `sample_assets/003_gunung_padang/003_gunung_padang_1.jpg` đến `..._6.jpg`), giúp quản lý cách ly tuyệt đối, không trùng lặp khi mở rộng hàng chục video.

---

## 3. Cách sử dụng

```bash
# Chạy với kịch bản và tự động đóng gói Caption + Video
python generate_video.py --script examples/script_dead_internet.json --output video_dead_internet.mp4

# Tùy biến tốc độ đọc nếu muốn (mặc định đã là +50% ~ 1.5x)
python generate_video.py --rate +30% --output video_thanh_pham.mp4
```
