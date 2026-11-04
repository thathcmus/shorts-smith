# Tài Liệu Thiết Kế Kỹ Thuật (Design Document)
## Tự Động Hóa Tài Nguyên Đầu Vào & Thiết Lập Bộ Kiểm Thử TDD (7_Media V2.5)

- **Ngày tạo:** 2026-11-04
- **Trạng thái:** DRAFT (Chờ phê duyệt)
- **Tác giả:** Trợ lý Kỹ thuật AI & Người phụ trách dự án

---

### 1. Bối cảnh & Mục đích (Intent & Why)

Dự án `7_Media` hiện tại là một hệ thống dựng video ngắn dạng dọc (9:16) hoàn thiện ở nửa sau của quy trình: tổng hợp giọng đọc Edge-TTS nhịp 1.5x, phụ đề động TikTok Karaoke, hiệu ứng máy quay điện ảnh Ken Burns, hòa âm BGM và đóng gói xuất bản.

Tuy nhiên, hệ thống đang bị thắt cổ chai nghiêm trọng ở **nửa đầu quy trình (Tài nguyên đầu vào)**:
- Người dùng vẫn phải tự viết kịch bản JSON 6 cảnh thủ công.
- Người dùng phải tự sao chép từng câu prompt tiếng Anh, tìm công cụ tạo ảnh, tải về và lưu vào thư mục `sample_assets/` từng file một.
- Mã nguồn chưa có bất kỳ bài kiểm thử tự động nào (0% Test Coverage), việc xử lý lỗi FFmpeg còn âm thầm (bỏ qua stderr vào `DEVNULL`), và các tệp âm thanh rác tạm thời còn tồn đọng ở thư mục gốc.

**Mục đích:** Tái cấu trúc hệ thống thành một pipeline tự hành khép kín:
**Chủ đề (Topic / Idea) ──> Tự sinh Kịch bản 6 cảnh ──> Tự sinh 6 Ảnh AI song song ──> Dựng Video & Bìa & Caption ──> Xuất bản**, kết hợp thiết lập bộ khung kiểm thử tự động theo chuẩn **Test-Driven Development (TDD)** và củng cố an toàn, bảo mật đường dẫn.

---

### 2. Mục tiêu, Phi mục tiêu & Ranh giới (Goals, Non-goals, Anti-goals)

#### Mục tiêu (Goals):
1. **Tự động sinh kịch bản (Script Generator):** Nhận 1 chủ đề bất kỳ (ví dụ: *"Bí ẩn Đảo Phục Sinh"*), tự động cấu trúc kịch bản 6 cảnh chuẩn tâm lý giật gân (Hook, Fact, Anomaly, Theory, Coincidence, CTA) kèm câu thoại tiếng Việt và visual prompt tiếng Anh cho từng cảnh.
2. **Tự động sinh ảnh AI song song (AI Image Generator):** Kết nối API đám mây miễn phí (Pollinations FLUX), tải bất đồng bộ (asyncio/aiohttp) song song cả 6 ảnh 1080x1920 chỉ trong 5-10 giây, tự kiểm tra ảnh hợp lệ và tự động lưu vào `sample_assets/{seq}_{slug}/`.
3. **Chạy 1 lệnh duy nhất (End-to-End CLI):** Hỗ trợ lệnh `python generate_video.py --topic "Chủ đề"` thực hiện toàn bộ quy trình từ ý tưởng đến thành phẩm đóng gói.
4. **An toàn & Dọn dẹp tài nguyên:** Thoát và bắt lỗi FFmpeg chi tiết (không giấu lỗi trong `DEVNULL`), escape an toàn đường dẫn tránh lỗi filter phụ đề, tự động dọn sạch thư mục tạm sau khi hoàn tất.
5. **Quy trình TDD hoàn chỉnh:** Xây dựng bộ test suite `pytest` kiểm thử độc lập từng module (có mock mạng để chạy offline trong < 3 giây), kiểm chứng mã nguồn trước khi tích hợp.

#### Phi mục tiêu (Non-goals):
- Không cài đặt mô hình AI nặng cục bộ (PyTorch/CUDA/ComfyUI) để giữ hệ thống siêu nhẹ, chạy được trên mọi môi trường mà không tốn dung lượng ổ cứng.
- Không thay đổi phong cách video hiện tại (vẫn giữ chuẩn 9:16, 6 cảnh, nhịp 1.5x, BGM điện ảnh, Karaoke vàng Neon).
- Không tự động đăng tải trực tiếp lên TikTok qua API (vẫn đóng gói trọn gói vào `output/publish_packages/` và quản lý tiến độ qua `STATUS.md`).

#### Ranh giới cảnh báo (Anti-goals):
- **Không dùng dịch vụ trả phí (F2P 100%):** Tuyệt đối không dùng API bắt buộc thẻ tín dụng hoặc nạp credit.
- **Không làm chậm tốc độ dựng:** Việc tạo 6 bức ảnh phải chạy song song, không tải tuần tự từng ảnh một.
- **Không phá vỡ tính tương thích ngược:** Các file kịch bản cũ (`examples/001_*.json` đến `006_*.json`) và cờ lệnh cũ (`-s 003`, `-s dead_internet`) vẫn phải hoạt động bình thường.

---

### 3. Các Phương án Kỹ thuật & Quyết định (Approaches & Decision)

#### Phương án 1: Kiến trúc Pipeline Module hóa phân tầng (ĐƯỢC CHỌN)
- **Cấu trúc:** Tách module `engine/image_generator.py` chuyên trách tải ảnh song song; nâng cấp `engine/script_generator.py` để sinh kịch bản từ chủ đề; nâng cấp `generate_video.py` để điều phối pipeline.
- **Ưu điểm:** Tách biệt trách nhiệm rõ ràng, tải ảnh cực nhanh, cực kỳ dễ viết Unit Test với TDD.
- **Đánh đổi:** Cần tạo thêm 1 file module mới.

#### Phương án 2: Tích hợp dồn vào tệp thực thi hiện có (Monolithic Inline - BỊ LOẠI BỎ)
- **Cấu trúc:** Viết toàn bộ hàm gọi API và tải ảnh trực tiếp trong `generate_video.py`.
- **Lý do loại bỏ:** Gây phình to mã nguồn, trộn lẫn logic mạng với logic dựng video FFmpeg, tải ảnh tuần tự chậm chạp và rất khó viết test tự động độc lập.

---

### 4. Thiết Kế Chi Tiết Kiến Trúc Hệ Thống (Detailed System Design)

#### 4.1. Module Sinh Ảnh AI Đám Mây (`engine/image_generator.py`)
- **Dịch vụ sử dụng:** Pollinations.ai FLUX REST API (100% miễn phí, không cần token/key, hỗ trợ độ phân giải tùy chọn, trả về nhị phân trực tiếp).
- **Hàm cốt lõi:**
  - `async def fetch_image(prompt: str, output_path: str, width: int = 1080, height: int = 1920, retries: int = 3) -> str`: Tải 1 ảnh, kiểm tra tính toàn vẹn (header JPEG/PNG, dung lượng > 10KB) bằng Pillow.
  - `async def generate_images_parallel(scenes: list, target_dir: str) -> list`: Sử dụng `asyncio.gather()` để kích hoạt tải cùng lúc tất cả các cảnh chưa có ảnh.

#### 4.2. Module Sinh Kịch Bản Thông Minh (`engine/script_generator.py`)
- **Hàm cốt lõi mới:**
  - `generate_script_from_topic(topic: str, style: str = "mystery") -> dict`:
    - Sử dụng bộ quy chuẩn Prompt chuyên biệt cho nội dung ngắn giữ chân người xem.
    - Ép khuôn đầu ra thành cấu trúc JSON chuẩn gồm 6 cảnh: `hook`, `fact1`, `anomaly`, `theory`, `coincidence`, `cta`.
    - Mỗi cảnh tự động bao gồm:
      - `text`: Câu thoại tiếng Việt nhịp nhanh, đanh thép.
      - `effect`: Hiệu ứng camera (`zoom_in_fast`, `pan_down`, `zoom_in_slow`, `zoom_out`).
      - `prompt`: Visual prompt tiếng Anh chi tiết cao (Cinematic, 8k, lighting, dark mood) để đưa sang module sinh ảnh.
    - Tích hợp sẵn cơ chế **Fallback Generator**: Nếu mất kết nối mạng, hệ thống tự động suy luận kịch bản dựa trên mẫu chủ đề có sẵn mà không bị crash.

#### 4.3. Nâng cấp Điều Phối Pipeline (`generate_video.py`)
- Bổ sung cờ CLI:
  - `--topic` / `-t`: Chủ đề video cần tạo tự động (ví dụ: `python generate_video.py -t "Kim Tự Tháp Rừng Amazon"`).
  - `--generate-images` / `-g`: Ép buộc sinh lại ảnh AI ngay cả khi đã có tệp ảnh sẵn.
- **Quản lý tài nguyên rác & FFmpeg an toàn:**
  - Mọi tệp tạm thời trong quá trình xử lý bắt buộc gom vào thư mục `temp_build/job_{timestamp}/`.
  - Dùng khối `finally:` để tự động xóa sạch các tệp phụ đề tạm, manifest, clip thô và tệp `.mp3` mồ côi.
  - Xử lý escape đường dẫn FFmpeg an toàn cho Windows (`:` thành `\:`, chuẩn hóa `/`).
  - Ghi nhận `stderr` của FFmpeg chi tiết khi lệnh thất bại, không để `DEVNULL` gây lỗi ngầm.

#### 4.4. Khung Kiểm Thử Tự Động TDD (`tests/`)
- Cài đặt `pytest` làm test runner chính.
- Cấu trúc thư mục kiểm thử:
  ```
  tests/
  ├── __init__.py
  ├── conftest.py                  # Fixtures và mock dữ liệu
  ├── test_image_generator.py      # Test tải ảnh, retry, phát hiện ảnh lỗi
  ├── test_script_generator.py     # Test sinh kịch bản 6 cảnh, validate schema, fallback
  ├── test_publisher.py            # Test logic cấp số thứ tự 001, 002 và parse slug
  └── test_render_safety.py        # Test escape đường dẫn FFmpeg và bắt lỗi
  ```
- **Quy tắc TDD:** Viết test trước -> Xác nhận test thất bại (RED) -> Viết mã tối thiểu để vượt qua test (GREEN) -> Tối ưu hóa mã nguồn (REFACTOR).

---

### 5. Những Quyết Định Dành Cho Lập Trình Viên (What's Left to the Builder)
- Lựa chọn cổng kết nối LLM văn bản miễn phí tối ưu cho `script_generator.py` (ưu đãi Pollinations Text / Hugging Face Router kèm Fallback nội bộ).
- Thiết lập chi tiết các mock HTTP request trong `conftest.py` để toàn bộ bộ test có thể chạy offline hoàn toàn độc lập với mạng Internet.
