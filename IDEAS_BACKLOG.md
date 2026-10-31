# 📌 KẾ HOẠCH NỘI DUNG & Ý TƯỞNG VIDEO (IDEAS BACKLOG)

> **Mục tiêu:** Sản xuất 4 video TikTok tiếp theo theo đúng phong cách **Mắt Sahara (Richat Structure / Atlantis)**: Chủ đề bí ẩn khảo cổ, địa chất kỳ lạ, có tọa độ kiểm chứng thực tế, nhịp dồn dập 40-48 giây, 6 phân cảnh, phụ đề TikTok Karaoke Dynamic và thumbnail tương phản cao.
> Tất cả kịch bản (`examples/00X_*.json`) và tài nguyên mẫu (`sample_assets/00X_*`) đều được **đánh số thứ tự 3 chữ số đồng bộ 1:1** với mã video và gói xuất bản.

---

## 📊 BẢNG THEO DÕI TIẾN ĐỘ SẢN XUẤT 2 NGÀY TỚI

| STT | Mã Video / Slug | Chủ đề chính | Ngày dự kiến | Trạng thái | Kịch bản JSON |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `001` | `dead_internet` | Thuyết Internet Đã Chết | Đã làm | 🟢 ĐÃ ĐĂNG | [001_script_dead_internet.json](file:///e:/7_Media/examples/001_script_dead_internet.json) |
| `002` | `mat_sahara_atlantis` | Cấu trúc Richat - Atlantis | Đã làm | 🟢 ĐÃ ĐĂNG | [002_script_mat_sahara_atlantis.json](file:///e:/7_Media/examples/002_script_mat_sahara_atlantis.json) |
| `003` | `gunung_padang_pyramid` | Kim Tự Tháp 25.000 năm Đông Nam Á | **Ngày 1** | 🟡 SẴN SÀNG | [003_script_gunung_padang.json](file:///e:/7_Media/examples/003_script_gunung_padang.json) |
| `004` | `derinkuyu_underground` | Thành phố ngầm 18 tầng Cappadocia | **Ngày 1** | 📝 DRAFT | [004_script_derinkuyu.json](file:///e:/7_Media/examples/004_script_derinkuyu.json) |
| `005` | `baalbek_megaliths` | Cự thạch 1.500 tấn đền Baalbek | **Ngày 2** | 📝 DRAFT | [005_script_baalbek.json](file:///e:/7_Media/examples/005_script_baalbek.json) |
| `006` | `gobekli_tepe` | Thánh địa 12.000 năm bị chôn vùi | **Ngày 2** | 📝 DRAFT | [006_script_gobekli_tepe.json](file:///e:/7_Media/examples/006_script_gobekli_tepe.json) |

*Ghi chú trạng thái:* 
- 📝 `DRAFT`: Đã có kịch bản JSON và danh sách prompt ảnh chuẩn.
- ⏳ `READY_TO_RENDER`: Đã có đủ ảnh trong `sample_assets/`, sẵn sàng chạy pipeline.
- 🟢 `ĐÃ ĐĂNG`: Video đã xuất bản và đăng tải thành công lên kênh TikTok.

---

## 🎬 CHI TIẾT 4 VIDEO Ý TƯỞNG

### 1. Video 003: Gunung Padang (Kim Tự Tháp 25.000 Năm Ngay Đông Nam Á)
* **Tọa độ / Địa điểm:** Cianjur, Tây Java, Indonesia (Google Earth: `-6.9939, 107.0562`).
* **Bằng chứng thật:** Radar xuyên đất GPR, định tuổi Carbon-14 công bố trên tạp chí khoa học quốc tế, phát hiện buồng rỗng ngầm bí mật.
* **Quy chuẩn Cover Thumbnail:**
  - **Badge:** `BÍ MẬT ĐÔNG NAM Á`
  - **Title:** `GUNUNG PADANG`
  - **Subtitle:** `KIM TỰ THÁP CỔ NHẤT THẾ GIỚI?`
  - **Style:** `neon_yellow`
* **File kịch bản:** [`examples/003_script_gunung_padang.json`](file:///e:/7_Media/examples/003_script_gunung_padang.json)
* **Hình ảnh mẫu yêu cầu:** `sample_assets/003_gunung_padang_1.jpg` đến `..._6.jpg`
* **Lệnh dựng video siêu nhanh bằng Index:**
  ```bash
  python generate_video.py -s 003
  # hoặc: python generate_video.py -s 3
  ```

---

### 2. Video 004: Thành Phố Ngầm Derinkuyu (Boong-ke 18 Tầng Tránh Thảm Họa)
* **Tọa độ / Địa điểm:** Cappadocia, Thổ Nhĩ Kỳ (Google Earth: `38.3736, 34.7347`).
* **Bằng chứng thật:** Di sản UNESCO, sâu 85 mét, 15.000 giếng thông khí, những tảng đá lăn khổng lồ chỉ khóa được từ BÊN TRONG.
* **Quy chuẩn Cover Thumbnail:**
  - **Badge:** `CẢNH BÁO`
  - **Title:** `THÀNH PHỐ NGẦM`
  - **Subtitle:** `TỔ TIÊN TRỐN THỨ GÌ TỪ BẦU TRỜI?`
  - **Style:** `fire_red`
* **File kịch bản:** [`examples/004_script_derinkuyu.json`](file:///e:/7_Media/examples/004_script_derinkuyu.json)
* **Hình ảnh mẫu yêu cầu:** `sample_assets/004_derinkuyu_1.jpg` đến `..._6.jpg`
* **Lệnh dựng video siêu nhanh bằng Index:**
  ```bash
  python generate_video.py -s 004
  # hoặc: python generate_video.py -s 4
  ```

---

### 3. Video 005: Đền Baalbek (Ai Nâng Được Tảng Đá 1.500 Tấn?)
* **Tọa độ / Địa điểm:** Thung lũng Beqaa, Li-băng (Google Earth: `34.0076, 36.2045`).
* **Bằng chứng thật:** Tảng đá "Stone of the Pregnant Woman" nặng hơn 1.000 - 1.500 tấn tại mỏ đá, móng đền Trilithon 800 tấn nâng cao 7 mét không dùng vữa.
* **Quy chuẩn Cover Thumbnail:**
  - **Badge:** `NGHỊCH LÝ VẬT LÝ`
  - **Title:** `ĐỀN BAALBEK`
  - **Subtitle:** `CÔNG NGHỆ BỊ LÃNG QUÊN?`
  - **Style:** `neon_yellow`
* **File kịch bản:** [`examples/005_script_baalbek.json`](file:///e:/7_Media/examples/005_script_baalbek.json)
* **Hình ảnh mẫu yêu cầu:** `sample_assets/005_baalbek_1.jpg` đến `..._6.jpg`
* **Lệnh dựng video siêu nhanh bằng Index:**
  ```bash
  python generate_video.py -s 005
  # hoặc: python generate_video.py -s 5
  ```

---

### 4. Video 006: Göbekli Tepe (Thánh Địa 12.000 Năm Bị Cố Tình Chôn Vùi)
* **Tọa độ / Địa điểm:** Şanlıurfa, Thổ Nhĩ Kỳ (Google Earth: `37.2231, 38.9225`).
* **Bằng chứng thật:** Niên đại 9.600 TCN (cổ hơn Ai Cập 7.000 năm), các trụ chữ T 50 tấn chạm nổi 3D động vật, dấu vết cố tình lấp đất chôn vùi toàn bộ quần thể.
* **Quy chuẩn Cover Thumbnail:**
  - **Badge:** `BÍ MẬT PHONG ẤN`
  - **Title:** `GÖBEKLI TEPE`
  - **Subtitle:** `VÌ SAO BỊ CHÔN VÙI CÓ CHỦ ĐÍCH?`
  - **Style:** `neon_yellow`
* **File kịch bản:** [`examples/006_script_gobekli_tepe.json`](file:///e:/7_Media/examples/006_script_gobekli_tepe.json)
* **Hình ảnh mẫu yêu cầu:** `sample_assets/006_gobekli_tepe_1.jpg` đến `..._6.jpg`
* **Lệnh dựng video siêu nhanh bằng Index:**
  ```bash
  python generate_video.py -s 006
  # hoặc: python generate_video.py -s 6
  ```

---

## 🛠️ QUY TRÌNH 3 BƯỚC SẢN XUẤT KHI BẮT ĐẦU LÀM MỖI VIDEO

1. **Bước 1 - Sinh ảnh:** Mở file kịch bản `examples/{seq}_script_{slug}.json`, copy các dòng `prompt` để tạo ảnh 9:16 rồi lưu vào `sample_assets/{seq}_{slug}_{1..6}.jpg`.
2. **Bước 2 - Render Video:** Chạy lệnh siêu ngắn theo số Index:
   ```bash
   python generate_video.py -s <INDEX>   # Ví dụ: python generate_video.py -s 003 hoặc -s 3
   ```
3. **Bước 3 - Đăng bài:** Lấy trọn bộ Video MP4, Caption SEO và Ảnh bìa Cover sẵn sàng tại:
   `output/publish_packages/{seq}_{slug}/`
