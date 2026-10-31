# 🎬 AI Media & Video Producer V2

Hệ thống sản xuất video AI ngắn (Shorts / Reels / TikTok) tự động, đạt chất lượng điện ảnh và tối ưu quy trình xuất bản trọn gói (**End-to-End Publishing Pipeline**) tại thư mục `7_Media`. Được thiết kế theo kiến trúc module hóa tinh gọn, chạy trực tiếp mà không cần cài đặt cồng kềnh, tích hợp sẵn bộ 3 Kỹ năng AI Assistant (Antigravity Skills).

---

## ✨ Điểm nổi bật & Tính năng V2

- 🎙️ **Giọng đọc Edge-TTS & Nhịp điệu 1.5x dồn dập:** Tích hợp bộ giọng đọc AI tự nhiên không tốn phí (`vi-VN-NamMinhNeural`, `vi-VN-HoaiMyNeural`, `en-US-ChristopherNeural`, `en-US-JennyNeural`). Mặc định tốc độ đọc `+50%` (~1.5x) dồn dập, sắc bén chuẩn xu hướng video giữ chân người xem trên TikTok.
- ✨ **Phụ đề TikTok Karaoke Dynamic (Word-by-word Highlight):** Đồng bộ chính xác từng từ thông qua `WordBoundary` của Edge-TTS. Từ đang đọc sẽ **bật sáng màu vàng Neon (`#00E5FF`)**, các từ còn lại mang màu trắng tinh khiết viền đen dày, hiển thị theo từng cụm 2-4 từ ở 1/3 dưới màn hình (chuẩn tầm mắt).
- 🎬 **Chuyển động Ken Burns & Cinematic Look:** Bộ lọc FFmpeg cao cấp kết hợp chuyển động camera mượt mà (Zoom in, Zoom out, Pan down/up/right) với **Color Grading** (tăng contrast, saturation) và **Vignette** (tối 4 góc màn hình điện ảnh). Hỗ trợ linh hoạt cả **Video Footage thực tế** lẫn **Hình ảnh tĩnh**.
- 🎵 **Hòa âm BGM Điện ảnh & Audio Ducking:** Tự động lựa chọn nhạc nền kịch tính từ kho `assets/audio/*.mp3`, lặp thông minh và tự động hạ âm lượng (ducking) vừa vặn khi có giọng đọc thuyết minh.
- 📦 **Không gian xuất bản trọn gói đánh số thứ tự tuần tự (`001_`, `002_`...):** Tự động phát hiện và cấp phát tiền tố số thứ tự 3 chữ số để **đối chiếu 1:1 tuyệt đối giữa Video và Caption**:
  - `output/{seq}_video_{slug}.mp4`: Video thành phẩm.
  - `output/cap/{seq}_cap_{slug}.txt`: File Caption TikTok chuẩn SEO (Tiêu đề in hoa, Hook, Kêu gọi bình luận CTA, và dàn Hashtags hot).
  - `output/covers/{seq}_cover_{slug}.jpg`: Ảnh bìa Thumbnail tỷ lệ 9:16 (1080x1920).
  - `output/publish_packages/{seq}_{slug}/`: Gói xuất bản độc lập chứa trọn bộ video, caption, cover và metadata JSON.
- 🎨 **Bộ thiết kế ảnh bìa chuyên nghiệp (TikTok Cover Designer):** Tự động trích xuất frame đắt giá từ video hoặc nhận ảnh tĩnh, phủ Typography Clickbait giật gân, viền bóng mờ, badge nền tối, căn chỉnh chuẩn **Safe Zone TikTok (32% - 48%)** để không bị giao diện che lấp.
- 📊 **Hệ thống theo dõi vòng đời xuất bản (Publishing Lifecycle Tracker):** Quản lý 3 trạng thái rõ ràng của từng video (`READY` 🟡, `POSTED` 🟢, `REJECTED` 🔴). Tự động cập nhật bảng điều khiển Markdown trực quan tại `output/STATUS.md` và cung cấp CLI tương tác.
- 🛡️ **Hệ thống thẩm định chất lượng QA & Git Diff (PR-Agent Style):** Tự động kiểm tra Git Diff, xác minh điểm gọi hàm (call-site integrity), kiểm tra thông số kỹ thuật thực tế của video (độ phân giải, fps, bitrate) và trích xuất frame ảnh xác thực trực quan trước khi nghiệm thu.

---

## 📁 Cấu trúc thư mục dự án

```
7_Media/
├── .agent/skills/                      # Bộ 3 Kỹ năng tích hợp cho AI Assistant
│   ├── ai-video-producer/              # Kỹ năng viết kịch bản 6 cảnh và sản xuất video V2
│   ├── tiktok-cover-designer/          # Kỹ năng thiết kế ảnh bìa TikTok chuẩn Safe Zone
│   └── git-diff-qa-reviewer/           # Kỹ năng review Git Diff & kiểm định chất lượng QA
├── assets/
│   └── audio/                          # Kho nhạc nền MP3 điện ảnh (tension, suspense)
├── engine/                             # Thư viện xử lý cốt lõi
│   ├── __init__.py                     # Package interface export toàn bộ hàm chính
│   ├── config.py                       # Cấu hình độ phân giải, FPS, giọng đọc, tốc độ đọc 1.5x
│   ├── cover_designer.py               # Mô-đun thiết kế ảnh bìa Typography TikTok & Safe Zone
│   ├── effects.py                      # Bộ lọc Ken Burns, Cinematic Color Grade & Vignette
│   ├── publisher.py                    # Cấp mã số thứ tự, tạo Caption TikTok & đóng gói package
│   ├── qa_inspector.py                 # Kiểm định Git Diff & trích xuất frame xác thực video
│   ├── render.py                       # Dựng clip cảnh, ghép nối video, hòa âm BGM và nung phụ đề
│   ├── script_generator.py             # Quản lý cấu trúc kịch bản 6 cảnh chuẩn viral
│   ├── status.py                       # Quản lý trạng thái xuất bản (READY, POSTED, REJECTED) & STATUS.md
│   └── tts.py                          # Edge-TTS WordBoundary & nung phụ đề TikTok Karaoke Dynamic
├── examples/                           # Kịch bản JSON mẫu hoàn chỉnh (đánh số 001_ đến 006_)
│   ├── 001_script_dead_internet.json       # Kịch bản: Thuyết Internet Chết (35s)
│   ├── 002_script_mat_sahara_atlantis.json # Kịch bản: Cấu trúc Richat - Atlantis (45s)
│   ├── 003_script_gunung_padang.json       # Kịch bản: Kim Tự Tháp 25.000 năm (45s)
│   ├── 004_script_derinkuyu.json           # Kịch bản: Thành phố ngầm 18 tầng (44s)
│   ├── 005_script_baalbek.json             # Kịch bản: Cự thạch 1.500 tấn (45s)
│   └── 006_script_gobekli_tepe.json        # Kịch bản: Göbekli Tepe chôn vùi (45s)
├── output/                             # Không gian xuất bản thành phẩm
│   ├── 001_video_dead_internet.mp4     # Video thành phẩm xuất ra gốc
│   ├── cap/                            # Thư mục chứa Caption chuẩn SEO ({seq}_cap_{slug}.txt)
│   ├── covers/                         # Thư mục chứa ảnh bìa Thumbnail ({seq}_cover_{slug}.jpg)
│   ├── publish_packages/               # Thư mục trọn gói xuất bản sẵn sàng đăng
│   │   └── 001_dead_internet/
│   │       ├── 001_video_dead_internet.mp4
│   │       ├── 001_cap_dead_internet.txt
│   │       ├── 001_cover_dead_internet.jpg
│   │       └── 001_metadata.json
│   ├── qa_verification/                # Frame trích xuất thẩm định chất lượng thực tế
│   └── STATUS.md                       # Bảng theo dõi tiến độ đăng video Markdown
├── sample_assets/                      # Kho hình ảnh / video footage mẫu
├── temp_build/                         # Thư mục tệp tạm thời trong lúc render
└── generate_video.py                   # Điểm vào CLI chính của hệ sinh thái
```

---

## ⚙️ Cài đặt & Yêu cầu môi trường

### 1. Yêu cầu hệ thống
- **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
- **Python:** Phiên bản `3.10` trở lên.
- **FFmpeg:** Tự động tích hợp sẵn thông qua gói `imageio-ffmpeg` (không cần cài đặt FFmpeg thủ công vào PATH hệ thống).

### 2. Cài đặt các thư viện phụ thuộc
Mở terminal tại thư mục `7_Media` và chạy lệnh sau:

```bash
pip install edge-tts imageio-ffmpeg pillow
```

> **Chi tiết các gói:**
> - `edge-tts`: Tổng hợp giọng nói Microsoft Edge Text-to-Speech chất lượng cao và bắt nhịp từng từ (`WordBoundary`).
> - `imageio-ffmpeg`: Cung cấp file thực thi FFmpeg nhị phân tối ưu cho môi trường hiện tại.
> - `pillow`: Xử lý đồ họa, typography, hiệu ứng bóng mờ và render ảnh bìa TikTok chuẩn kích thước.

---

## 🚀 Hướng dẫn sử dụng chi tiết các câu lệnh (CLI Reference)

Hệ thống cung cấp 4 công cụ dòng lệnh chuyên biệt phục vụ toàn bộ chu trình sản xuất - thiết kế - theo dõi - kiểm định:

```
[1. generate_video.py] ──> [2. engine.cover_designer] ──> [3. engine.status] ──> [4. engine.qa_inspector]
     (Dựng video)               (Thiết kế ảnh bìa)            (Quản lý đăng)             (Kiểm định QA)
```

---

### 1. Dựng Video Tự Động (`generate_video.py`)

Điểm vào chính để tổng hợp giọng đọc, hiệu ứng camera, nung phụ đề TikTok Karaoke và đóng gói xuất bản.

#### Cú pháp:
```bash
python generate_video.py [TÙY CHỌN]
```

#### Bảng tham số chi tiết:
| Tham số | Viết tắt | Mặc định | Ý nghĩa & Ví dụ |
| :--- | :---: | :--- | :--- |
| `--script` | `-s` | Tự động | **Index kịch bản** (`1`, `001`, `3`, `003`...) hoặc từ khóa slug (`gunung_padang`) hoặc đường dẫn file JSON |
| `--output` | `-o` | Tự sinh theo kịch bản | Tên tệp video xuất ra (tự động nhận diện từ kịch bản dạng `{seq}_video_{slug}.mp4`) |
| `--voice` | `-v` | `vi-VN-NamMinhNeural` | Tên giọng đọc Edge-TTS (`vi-VN-NamMinhNeural`, `vi-VN-HoaiMyNeural`, `en-US-ChristopherNeural`, `en-US-JennyNeural`) |
| `--rate` | `-r` | `+50%` | Tốc độ giọng đọc thuyết minh (`+50%` ~ 1.5x TikTok, `+30%`, `+0%`) |
| `--bgm` | `-b` | Tự chọn từ `assets/audio/*.mp3` | Đường dẫn tệp nhạc nền MP3 riêng |
| `--bgm-volume` | | `0.22` | Âm lượng nhạc nền (từ `0.0` đến `1.0`, mặc định `0.22` vừa vặn tôn giọng thuyết minh) |
| `--aspect` | `-a` | `vertical` | Tỉ lệ khung hình: `vertical` (9:16 - 1080x1920 cho TikTok/Reels) hoặc `horizontal` (16:9 - 1920x1080 cho YouTube chuẩn) |

#### Các ví dụ thực tế:

```bash
# 1. Chạy siêu ngắn bằng số Index (tự nhận diện kịch bản và tự đặt tên video 003_video_gunung_padang.mp4)
python generate_video.py -s 003
# hoặc: python generate_video.py -s 3

# 2. Sử dụng giọng đọc nữ truyền cảm với kịch bản Mắt Sahara bằng Index 002
python generate_video.py -s 002 --voice vi_nu

# 3. Điều chỉnh tốc độ đọc 1.3x (+30%) và dùng nhạc nền riêng
python generate_video.py -s 001 --rate +30% --bgm assets/audio/tension_track.mp3

# 4. Vẫn hỗ trợ truyền đường dẫn file JSON trực tiếp như cũ
python generate_video.py --script examples/003_script_gunung_padang.json
```

> **Sau khi lệnh hoàn tất, hệ thống tự động sinh ra:**
> - Video: `output/001_video_dead_internet.mp4`
> - Caption: `output/cap/001_cap_dead_internet.txt`
> - Gói xuất bản: `output/publish_packages/001_dead_internet/`
> - Bảng trạng thái: `output/STATUS.md` được cập nhật tự động sang trạng thái `READY`.

---

### 2. Thiết Kế & Nâng Cấp Ảnh Bìa TikTok (`engine.cover_designer`)

Thiết kế ảnh bìa (Thumbnail 1080x1920) chuẩn Viral TikTok, áp dụng công thức giật gân, viền bóng mờ và căn chỉnh trong **Safe Zone**.

#### Cú pháp:
```bash
python -m engine.cover_designer [TÙY CHỌN]
```

#### Bảng tham số chi tiết:
| Tham số | Viết tắt | Bắt buộc | Ý nghĩa |
| :--- | :---: | :---: | :--- |
| `--id` | | Không | Số thứ tự video trong kho (ví dụ: `001`, `002`) để trích xuất frame từ video đó và tự động đồng bộ ảnh bìa vào `output/covers/` lẫn `output/publish_packages/` |
| `--video` | `-v` | Không | Đường dẫn file video MP4 nguồn nếu không dùng `--id` |
| `--image` | `-i` | Không | Đường dẫn file ảnh tĩnh nguồn nếu không dùng video |
| `--title` | `-t` | **Có** | Tiêu đề giật gân chính in hoa (cú đấm thị giác 2-4 từ, ví dụ: `"INTERNET ĐÃ CHẾT?"`) |
| `--subtitle` | `-s` | Không | Dòng giải thích phụ gây tò mò (ví dụ: `"90% MẠNG XÃ HỘI LÀ BOT AI"`) |
| `--badge` | `-b` | Không | Tag nhỏ làm nổi bật trên cùng (ví dụ: `"SỰ THẬT"`, `"BÍ MẬT"`, `"CẢNH BÁO"`) |
| `--style` | | Không | Phong cách màu sắc: `neon_yellow` (vàng neon - khuyên dùng), `fire_red` (đỏ cảnh báo), `clean_white` (trắng tinh khiết). Mặc định: `neon_yellow` |
| `--time` | | Không | Giây trích xuất frame từ video nguồn (mặc định: `2.5`s) |
| `--output` | `-o` | Không | Đường dẫn file ảnh xuất ra (mặc định lưu vào `output/covers/`) |

#### Các ví dụ thực tế:

```bash
# 1. Thiết kế lại ảnh bìa giật gân cho video 001 đã có trong kho xuất bản
python -m engine.cover_designer --id 001 --badge "BÍ MẬT ĐEN TỐI" --title "INTERNET ĐÃ CHẾT?" --subtitle "90% MẠNG XÃ HỘI LÀ BOT AI" --style neon_yellow

# 2. Thiết kế ảnh bìa phong cách đỏ cảnh báo cho video 002
python -m engine.cover_designer --id 002 --badge "CẢNH BÁO" --title "MẮT SAHARA" --subtitle "ATLANTIS ĐÃ ĐƯỢC TÌM THẤY?" --style fire_red

# 3. Tạo ảnh bìa từ một ảnh tĩnh bất kỳ
python -m engine.cover_designer --image sample_assets/richat.jpg --badge "BÍ ẨN CỔ ĐẠI" --title "THÀNH PHỐ MẤT TÍCH" --subtitle "BÍ MẬT 10.000 NĂM TRƯỚC" --output output/covers/custom_atlantis.jpg
```

---

### 3. Quản Lý Tiến Độ & Vòng Đời Xuất Bản (`engine.status`)

Theo dõi trạng thái của toàn bộ video đã sản xuất qua 3 trạng thái:
- 🟡 `READY`: Video đã dựng xong, caption đã sẵn sàng, chờ đăng.
- 🟢 `POSTED`: Đã đăng tải thành công lên kênh TikTok (kèm ngày giờ và link video thực tế).
- 🔴 `REJECTED`: Video bị hủy hoặc lưu trữ nội bộ (kèm lý do ghi chú).

#### Cú pháp:
```bash
# Xem bảng trạng thái tổng quan trong Terminal
python -m engine.status list

# Cập nhật trạng thái video theo số thứ tự (ví dụ: 001) hoặc slug
python -m engine.status set <ID> <STATUS> [--url <LINK_TIKTOK>] [--note <GHI_CHÚ>]
```

#### Các ví dụ thực tế:

```bash
# 1. Liệt kê danh sách tất cả video và trạng thái hiện tại
python -m engine.status list

# 2. Đánh dấu video 001 ĐÃ ĐĂNG lên kênh TikTok (kèm link bài đăng)
python -m engine.status set 001 POSTED --url "https://www.tiktok.com/@kenh_cua_ban/video/7702664039482051841"

# 3. Đánh dấu video 002 ĐÃ ĐĂNG
python -m engine.status set 002 POSTED --url "https://www.tiktok.com/@kenh_cua_ban/video/7702665379180580104"

# 4. Đánh dấu một video KHÔNG ĐĂNG (bị hủy hoặc ý tưởng chưa phù hợp)
python -m engine.status set 003 REJECTED --note "Kịch bản cần sửa đổi thêm phần hook"

# 5. Đặt lại trạng thái READY (Sẵn sàng đăng lại)
python -m engine.status set 001 READY
```

> **Tự động đồng bộ:** Mỗi khi chạy lệnh `set`, hệ thống tự động cập nhật lại bảng điều khiển Markdown cực đẹp tại `output/STATUS.md`.

---

### 4. Kiểm Định Chất Lượng QA & Git Diff (`engine.qa_inspector`)

Bộ công cụ kiểm định chất lượng lấy cảm hứng từ PR-Agent. Ngăn ngừa việc "bình mới rượu cũ", tự động phân tích Git Diff, xác minh các hàm mới có thực sự được gọi ở điểm thực thi hay không, và trích xuất frame thực tế từ video để nghiệm thu phụ đề, hiệu ứng màu sắc.

#### Cú pháp:
```bash
python -m engine.qa_inspector [ĐƯỜNG_DẪN_VIDEO]
```

#### Các ví dụ thực tế:

```bash
# Kiểm tra Git Diff và nghiệm thu chất lượng video thành phẩm
python -m engine.qa_inspector output/001_video_dead_internet.mp4

# Kiểm tra chất lượng video 002
python -m engine.qa_inspector output/002_video_mat_sahara_atlantis.mp4
```

> **Kết quả đầu ra:**
> - Báo cáo số dòng mã thay đổi (+ / -).
> - Kiểm tra thông số video thực tế: Tên file, dung lượng (MB), độ phân giải (1080x1920), thời lượng chính xác, luồng âm thanh AAC.
> - Trích xuất 1 ảnh tĩnh tại giây thứ 4 vào `output/qa_verification/verified_frame_sample.jpg` để trực tiếp kiểm tra phụ đề Karaoke và hiệu ứng Vignette.

---

## 🤖 Điều khiển qua AI Assistant (Chat Prompting)

Nếu bạn sử dụng Antigravity IDE hoặc AI Assistant có hỗ trợ Skill, bạn không cần phải gõ lệnh thủ công. Chỉ cần nhập các câu lệnh tự nhiên trong khung chat:

### 1. Kích hoạt Kỹ năng Sản xuất Video (`ai-video-producer`)
- *"Tạo video ngắn 60s về chủ đề Bí ẩn Thuyết Internet Chết."*
- *"Làm một video TikTok về Cấu trúc Mắt Sahara và nền văn minh Atlantis bị chôn vùi."*
- *"Tạo kịch bản và xuất video về Sự thật rùng mình bên trong Đại Kim Tự Tháp Giza."*
👉 *AI sẽ tự động áp dụng công thức 6 cảnh, viết kịch bản giật gân, tổng hợp giọng nói, nung phụ đề Karaoke, hòa âm BGM và đóng gói Caption.*

### 2. Kích hoạt Kỹ năng Thiết kế Ảnh Bìa (`tiktok-cover-designer`)
- *"Thiết kế ảnh bìa TikTok giật gân cho video 001 phong cách neon_yellow."*
- *"Làm thumbnail cho video Mắt Sahara với tiêu đề MẮT SAHARA, phụ đề ATLANTIS LỘ DIỆN? theo tông màu fire_red."*
👉 *AI sẽ phân tích nội dung, trích xuất frame đắt giá tại Safe Zone và lưu ảnh bìa chuẩn 1080x1920.*

### 3. Kích hoạt Kỹ năng Theo dõi & Cập nhật Trạng thái
- *"Đánh dấu video 001 đã đăng lên TikTok với link: https://www.tiktok.com/@kenh/video/12345."*
- *"Kiểm tra danh sách trạng thái các video hiện tại xem video nào chưa đăng."*
👉 *AI sẽ gọi `engine.status` và báo cáo lại bảng tổng kết.*

### 4. Kích hoạt Kỹ năng Kiểm định QA (`git-diff-qa-reviewer`)
- *"Review git diff và kiểm tra chất lượng video 001 giúp tôi."*
👉 *AI sẽ kiểm tra Git Diff, quét thông số video, trích xuất frame và xuất báo cáo nghiệm thu.*

---

## 📝 Định dạng Tệp Kịch Bản JSON (Script Format)

Hệ thống cho phép bạn tùy biến toàn bộ nội dung kịch bản qua tệp JSON. Cấu trúc kịch bản chuẩn gồm danh sách các cảnh (`scenes`), tối ưu nhất là công thức 6 cảnh giữ chân người xem:

```json
{
  "scenes": [
    {
      "role": "hook",
      "text": "Có bao giờ bạn nhận ra... mạng Internet gần như đã chết từ nhiều năm trước?",
      "media": "sample_assets/matrix_code.jpg",
      "effect": "zoom_in_fast",
      "rate": "+50%"
    },
    {
      "role": "scale",
      "text": "Một báo cáo bảo mật chỉ ra rằng, hơn 60% lưu lượng truy cập toàn cầu hiện nay không hề đến từ con người.",
      "media": "sample_assets/botnet.jpg",
      "effect": "pan_down",
      "rate": "+50%"
    },
    {
      "role": "anomaly",
      "text": "Hàng triệu tài khoản mạng xã hội đang tự động đăng bài, tự động bình luận và tự thả tim cho nhau.",
      "media": "sample_assets/server_room.jpg",
      "effect": "zoom_in_slow",
      "rate": "+50%"
    },
    {
      "role": "theory",
      "text": "Giả thuyết Internet Chết cho rằng các tập đoàn công nghệ lớn đang dùng AI để tạo ra một thế giới ảo giả lập.",
      "media": "sample_assets/ai_brain.jpg",
      "effect": "zoom_out",
      "rate": "+50%"
    },
    {
      "role": "coincidence",
      "text": "Mục đích là thao túng hành vi mua sắm và định hình nhận thức của phần ít ỏi người thật còn sót lại.",
      "media": "sample_assets/puppet.jpg",
      "effect": "zoom_in_slow",
      "rate": "+50%"
    },
    {
      "role": "cta",
      "text": "Bạn có chắc người đang tranh luận với bạn hôm nay là con người? Hãy để lại suy nghĩ dưới bình luận!",
      "media": "sample_assets/human_silhouette.jpg",
      "effect": "zoom_in_fast",
      "rate": "+50%"
    }
  ]
}
```

### Các thuộc tính của mỗi cảnh:
- `text` *(bắt buộc)*: Câu thoại thuyết minh.
- `media` *(bắt buộc)*: Đường dẫn tới file ảnh (`.jpg`, `.png`) hoặc file video clip ngắn (`.mp4`).
- `effect` *(tùy chọn)*: Hiệu ứng camera Ken Burns cho ảnh tĩnh:
  - `zoom_in_fast`: Zoom cận cảnh nhanh (phù hợp mở màn Hook và kết màn CTA).
  - `zoom_in_slow`: Zoom chậm kịch tính, lôi cuốn chiều sâu.
  - `zoom_out`: Thu rộng khung cảnh, tạo cảm giác choáng ngợp hoặc bí ẩn vĩ mô.
  - `pan_down`: Lia máy từ trên xuống dưới (phù hợp hiển thị quy mô, kích thước khổng lồ).
  - `pan_up`: Lia máy từ dưới lên trên.
  - `pan_right`: Lia máy ngang sang phải.
- `rate` *(tùy chọn)*: Tốc độ đọc riêng cho từng cảnh (ví dụ: `+50%`, `+30%`). Mặc định lấy theo tốc độ chung của dự án.

---

## 🎯 Quy chuẩn Tối ưu Video TikTok Viral

1. **Vùng an toàn (Safe Zone) 9:16:**
   - **Đỉnh (0% - 15%):** Nút Tìm kiếm & tab Đang theo dõi.
   - **Cột phải (85% - 100%):** Nút Tim, Bình luận, Chia sẻ, Âm thanh.
   - **Đáy (70% - 100%):** Tên tài khoản, mô tả Caption, hashtag.
   - 👉 **Vùng vàng đặt Tiêu đề bìa (Cover Title):** Từ **32% đến 48%** chiều cao màn hình.
   - 👉 **Vùng đặt Phụ đề động (Karaoke Subtitles):** Nằm ở khoảng **1/3 dưới** màn hình (`MarginV=450` trên khung 1080x1920).
2. **Quy tắc 3 Giây Đầu (The 3s Hook):**
   - Luôn bắt đầu bằng một câu hỏi phản trực giác hoặc khẳng định gây sốc.
   - Tốc độ đọc mở màn dồn dập (1.5x) kết hợp hiệu ứng `zoom_in_fast` để giật lấy sự chú ý.
3. **Đóng gói Caption chuẩn SEO:**
   - Mỗi video đều đi kèm file `{seq}_cap_{slug}.txt` chứa sẵn: Tiêu đề in hoa giật gân, Hook mở màn, Câu hỏi kích thích tranh luận CTA và bộ Hashtags chuẩn xu hướng (`#learnontiktok`, `#xuhuong`, `#viral`...). Bạn chỉ cần mở lên và sao chép thẳng vào ứng dụng TikTok khi đăng.

---

## 📄 Bản quyền & Đóng góp
Dự án được xây dựng và phát triển nội bộ phục vụ sản xuất truyền thông đa nền tảng tự động chất lượng cao. Mọi đóng góp, cải tiến hiệu ứng hoặc bổ sung kịch bản mẫu vui lòng gửi Pull Request hoặc cập nhật thông qua bộ Kỹ năng AI tích hợp.
