---
name: tiktok-cover-designer
description: >-
  Thiết kế ảnh bìa (Cover / Thumbnail 9:16 - 1080x1920) chuyên nghiệp chuẩn phong cách Viral TikTok / Reels / Shorts.
  Tự động chọn frame đắt giá từ video hoặc ảnh nền, áp dụng nguyên tắc Typography giật gân (Clickbait Headline, màu Neon tương phản cao, badge nền tối)
  chuẩn Safe Zone tránh che lấp bởi giao diện TikTok, đồng bộ trực tiếp ra thư mục output/covers/ và output/publish_packages/.
---

# Kỹ năng Thiết Kế Ảnh Bìa TikTok (TikTok Cover Designer Skill)

Skill này cung cấp quy trình chuyên biệt giúp AI Assistant và Creator thiết kế ảnh bìa (Cover / Thumbnail) tỷ lệ 9:16 đạt tỷ lệ nhấp (Click-Through Rate - CTR) cao nhất trên TikTok, YouTube Shorts và Instagram Reels.

---

## 1. Nguyên tắc thiết kế ảnh bìa chuẩn Viral TikTok

### 🎯 Quy tắc Safe Zone (Vùng an toàn giao diện TikTok):
Giao diện người dùng của TikTok che phủ rất nhiều phần của màn hình:
* **Đỉnh màn hình (0% - 15%):** Nút Tìm kiếm, tab "Đang theo dõi / Dành cho bạn".
* **Cột bên phải (85% - 100% chiều ngang):** Avatar kênh, nút Tim, Bình luận, Lưu, Chia sẻ.
* **Đáy màn hình (70% - 100% chiều cao):** Tên tài khoản, nội dung Caption, tên bài hát và thanh điều hướng.
👉 **VÙNG AN TOÀN ĐẶT TIÊU ĐỀ BÌA:** Nằm ở khoảng **32% đến 48% tính từ trên xuống**, căn giữa màn hình (Center Horizontally) với lề hai bên tối thiểu 40px.

---

### 💥 Công thức Tiêu đề Giật Gân (Clickbait Headline Formula):
Tiêu đề bìa KHÔNG PHẢI là tóm tắt dài dòng, mà là **cú đấm thị giác (Visual Punch)** khiến người xem phải dừng ngón tay lại:

1. **Công thức Phủ định niềm tin (Curiosity Gap):**
   * Ví dụ: `INTERNET ĐÃ CHẾT?`, `KIM TỰ THÁP KHÔNG PHẢI LĂNG MỘ?`, `TRÁI ĐẤT KHÔNG HỀ HÌNH CẦU?`
2. **Công thức Con số / Tỷ lệ chấn động:**
   * Ví dụ: `90% LÀ BOT AI`, `BÍ MẬT 10.000 NĂM`, `1 THẾ LỰC NẮM 99% TIỀN`
3. **Công thức Cảnh báo / Bí mật bị cấm:**
   * Ví dụ: `ĐỪNG ĐẾN ĐÂY!`, `BÍ MẬT BỊ GIẤU KÍN`, `SỰ THẬT RÙNG MÌNH`

---

### 🎨 Bảng phối màu tương phản cao (High Contrast Styles):
* **Neon Yellow (`neon_yellow` - Khuyên dùng):** Tiêu đề chữ vàng chanh neon rực rỡ (`#FFE600`), phụ đề chữ trắng, viền đen dày 7px, đặt trên nền hộp mờ (Dark Box Pill).
* **Fire Red (`fire_red`):** Tiêu đề chữ đỏ cảnh báo (`#FF2D2D`), phụ đề chữ vàng, viền đen dày, thích hợp cho chủ đề kinh dị, thảm họa, nguy hiểm.
* **Clean White (`clean_white`):** Tiêu đề chữ trắng tinh khiết viền đen, phụ đề chữ vàng neon, thích hợp cho chủ đề khoa học, công nghệ, tương lai.

---

## 2. Quy trình thiết kế ảnh bìa cho AI Assistant

Khi người dùng yêu cầu:
* *"Thiết kế ảnh bìa cho video 001"*
* *"Làm thumbnail TikTok cho video Mắt Sahara"*
* *"Tạo cover giật gân về chủ đề Kim Tự Tháp"*

Hãy thực hiện theo 3 bước:

### Bước 1: Xác định nguồn video / hình ảnh và phân tích kịch bản
* Kiểm tra video trong `output/` hoặc `output/publish_packages/` (thông qua mã số `001`, `002`... hoặc slug).
* Đọc nhanh nội dung kịch bản hoặc hook của video để chắt lọc ra:
  * **Badge Tag (1-2 từ):** VD: `SỰ THẬT`, `BÍ MẬT`, `KHOA HỌC`, `NGUY HIỂM`.
  * **Title chính (2-4 từ in hoa):** Câu hỏi hoặc từ khóa bùng nổ nhất.
  * **Subtitle phụ (3-6 từ in hoa):** Dòng bổ trợ gây tò mò cực độ.

### Bước 2: Chạy công cụ CLI thiết kế ảnh bìa
Sử dụng công cụ `engine.cover_designer`:

```bash
# Thiết kế hoặc cập nhật lại ảnh bìa cho video đã có sẵn theo ID:
python -m engine.cover_designer --id 001 --badge "BÍ MẬT ĐEN TỐI" --title "INTERNET ĐÃ CHẾT?" --subtitle "90% MẠNG XÃ HỘI LÀ BOT AI" --style neon_yellow

# Hoặc tạo ảnh bìa từ một ảnh tĩnh trong thư mục sample_assets:
python -m engine.cover_designer --image sample_assets/richat.jpg --badge "BÍ ẨN ĐẠI DƯƠNG" --title "MẮT SAHARA" --subtitle "ATLANTIS ĐÃ ĐƯỢC TÌM THẤY?" --output output/covers/002_cover_mat_sahara_atlantis.jpg
```

### Bước 3: Đồng bộ và kiểm tra kết quả
* File ảnh bìa hoàn tất sẽ tự động xuất hiện tại:
  1. `output/covers/{seq}_cover_{slug}.jpg`: Mở xem và lấy nhanh khi đăng tải.
  2. `output/publish_packages/{seq}_{slug}/{seq}_cover_{slug}.jpg`: Đồng bộ trọn gói.
* Báo cáo cho người dùng đường dẫn file ảnh bìa kèm thông số.

---

## 3. Các tùy chọn dòng lệnh chính của `engine.cover_designer`

| Tham số | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| `--id` | Số thứ tự video trong kho xuất bản | `--id 001` |
| `--title`, `-t` | Tiêu đề chính in hoa (bắt buộc) | `--title "INTERNET ĐÃ CHẾT?"` |
| `--subtitle`, `-s` | Dòng mô tả ngắn phụ | `--subtitle "90% MẠNG XÃ HỘI LÀ BOT AI"` |
| `--badge`, `-b` | Tag nhỏ trên cùng | `--badge "CẢNH BÁO"` |
| `--style` | Bộ màu: `neon_yellow`, `fire_red`, `clean_white` | `--style neon_yellow` |
| `--time` | Thời điểm trích xuất frame từ video (giây) | `--time 2.5` |
| `--image`, `-i` | Đường dẫn file ảnh tĩnh nếu không dùng video | `--image sample_assets/bg.jpg` |
| `--output`, `-o` | Đường dẫn file ảnh xuất ra | `--output output/covers/custom.jpg` |
