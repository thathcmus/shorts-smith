---
name: git-diff-qa-reviewer
description: >-
  Tự động review và thẩm định các thay đổi mã nguồn (Git Diff) cùng chất lượng sản phẩm đầu ra
  (Output Verification) dựa trên triết lý của PR-Agent. Ngăn chặn việc 'bình mới rượu cũ',
  tự động đối chiếu diff lines, kiểm tra tính toàn vẹn của logic gọi hàm, và trích xuất kiểm định
  thực tế (frame/audio) trước khi báo cáo hoàn thành.
---

# Kỹ năng Thẩm Định Thay Đổi & Kiểm Tra Đầu Ra (Git Diff & QA Verifier)
*Học hỏi và kế thừa từ dự án PR-Agent (Qodo/CodiumAI)*

Skill này cung cấp quy chuẩn kiểm định nghiêm ngặt cho AI Assistant trước khi bàn giao bất kỳ tính năng, bản sửa đổi hay sản phẩm nào cho người dùng.

---

## 1. Nguyên Tắc Cốt Lõi (PR-Agent Philosophy)

1. **Không tin vào Exit Code 0 đơn thuần:**
   - Một lệnh chạy không báo lỗi (`exit code 0`) không đồng nghĩa với việc nó đã cho ra sản phẩm đúng chất lượng mới.
2. **Kiểm tra tính toàn vẹn điểm gọi hàm (Call-Site Integrity):**
   - Khi tạo module/hàm mới (ví dụ: `new_feature()`), bắt buộc phải kiểm tra trong Git Diff xem hàm đó **ĐÃ ĐƯỢC GỌI** ở file thực thi chính hay chưa. Tránh trường hợp viết code mới nhưng file chạy vẫn gọi logic cũ.
3. **Thẩm định sản phẩm thực tế (Tangible Output Verification):**
   - Với Media/Video: Phải dùng `ffprobe`/`ffmpeg` kiểm tra thông số và chụp frame mẫu tại các giây quan trọng để xác thực trực quan (phụ đề, màu sắc, âm thanh).
   - Với Code/API: Phải chạy test thực tế và kiểm tra dữ liệu trả về thực sự.

---

## 2. Quy Trình 4 Bước Thẩm Định Bắt Buộc

Mỗi khi agent hoàn thành một tác vụ nâng cấp code hoặc tạo sản phẩm:

```
[BƯỚC 1: GIT DIFF AUDIT] -> [BƯỚC 2: CALL-SITE CHECK] -> [BƯỚC 3: OUTPUT PROBE] -> [BƯỚC 4: VERIFIED REPORT]
```

### Bước 1: Soi Diff (`git diff`)
- Liệt kê các dòng mã mới thêm (`+`) và các dòng loại bỏ (`-`).
- Kiểm tra xem có code thừa hoặc logic cũ chưa xóa không.

### Bước 2: Kiểm tra điểm gọi hàm
- Xác nhận các file thực thi chính (`generate_video.py`, `main.py`) đang import và gọi trực tiếp các module mới vừa viết.

### Bước 3: Kiểm định sản phẩm thực tế
Chạy công cụ kiểm tra tự động:
```bash
python -m engine.qa_inspector output/video_thanh_pham.mp4
```
Hệ thống sẽ:
* Đo đạc chính xác độ phân giải, luồng âm thanh, bitrate.
* Chụp 1 ảnh tĩnh trích xuất từ video tại giây thứ 4 để làm bằng chứng xác thực.

### Bước 4: Xuất báo cáo Before vs After
Báo cáo cho người dùng phải nêu rõ:
- Trước đây: Cơ chế cũ là gì?
- Hiện tại: Cơ chế mới là gì?
- Bằng chứng kiểm định: File ảnh/thông số thực tế chứng minh tính năng mới đã hoạt động.
