# Claim-level scientific review and evidence policy v1.0

**Trạng thái:** v1.0 (2026-10-14), thay cho bản baseline. Công cụ kiểm tra tự động: `src/sma/claims.py` (`python3 -m sma.claims episodes/<id>/claims.csv`).

## 1. Thang bằng chứng (ưu tiên từ cao xuống thấp)

1. Nghiên cứu gốc có bình duyệt, hoặc công bố thực nghiệm chính thức (cho claim thực nghiệm hẹp).
2. Giá trị chuẩn hoặc định nghĩa của tổ chức chuẩn hóa: **NIST/CODATA, IAU, IUPAC, BIPM**.
3. Review có hệ thống, giáo trình lớn, tuyên bố đồng thuận.
4. Trang giải thích của cơ quan khoa học hoặc đại học uy tín: **NASA/JPL, ESA, CERN, NIH**.
5. Báo chí khoa học biên tập tốt: chỉ dùng để tìm manh mối, không làm nguồn duy nhất cho cơ chế còn tranh cãi.
6. Blog cá nhân, Wikipedia, YouTube: chỉ để khám phá và bối cảnh, **không bao giờ là nguồn duy nhất cho claim khoa học quan trọng**.

Ngoại lệ: kết quả toán học có thể dựa vào chứng minh hoặc giáo trình chuẩn. Phép tính (`DERIVED`) phải ghi rõ công thức và nguồn của từng đầu vào. Claim lịch sử cần sử liệu gốc hoặc công trình học thuật. Preprint phải gắn `PREPRINT` ở cột `evidence_type`.

## 2. Claim ledger: `episodes/<id>/claims.csv`

Một dòng cho mỗi khẳng định khoa học quan trọng. Các cột (đúng thứ tự, `sma.claims` kiểm tra):

| Cột | Bắt buộc | Nội dung |
|---|---|---|
| `claim_id` | ✔ | `C001`… Phải xuất hiện dưới dạng `[C001]` trong `script.md` |
| `claim_vi` | ✔ | Câu tiếng Việt **đúng như trong kịch bản** (hoặc mệnh đề cốt lõi) |
| `category` | ✔ | Một nhãn trong EDITORIAL_GUIDE §4 |
| `evidence_type` | ✔ | `standard`, `peer_reviewed`, `review`, `textbook`, `institutional`, `historical_primary`, `historical_secondary`, `calculation`, `PREPRINT`, `none` |
| `source_ids` | ✔ (trừ FICTION/ANALOGY) | `S01;S03`, tham chiếu `sources.md` |
| `doi` | nếu có | |
| `supporting_location` | ✔ | Đoạn, mục hay bảng **cụ thể** hỗ trợ claim. Với phép tính thì ghi công thức |
| `confidence` | ✔ | `high` / `medium` / `low` |
| `assumptions` | | Giả định cần để claim đúng |
| `limitations` | | Giới hạn, điều kiện, điểm tranh luận |
| `reviewer_status` | ✔ | `PENDING`, `APPROVED`, `REVISED`, `REJECTED` |
| `reviewer_note` | | Nhận xét của reviewer độc lập |

Chỉ có link nguồn là chưa đủ: phải ghi **phần cụ thể** hỗ trợ claim. `FICTION` và `ANALOGY` không cần nguồn, nhưng kịch bản phải báo hiệu rõ cho người nghe.

## 3. Khi các nguồn mâu thuẫn

Ghi vào cột `limitations` và `sources.md`, phân tích nguyên nhân: khác phương pháp đo, khác mô hình, khác thời điểm hay epoch, khác điều kiện thí nghiệm, khác quy ước (ví dụ khoảng cách trung bình hay tức thời), hoặc khác mức đồng thuận. Nếu không giải quyết được thì không dùng con số đó làm trung tâm, hoặc trình bày dưới dạng khoảng giá trị.

## 4. Quy trình

1. Research agent lập 3–10 nguồn trong `sources.md` (ID, URL, DOI, loại, ngày truy cập, đoạn trích ngắn hoặc vị trí) và bản nháp claim ledger.
2. Scriptwriter viết kịch bản gốc, gắn `[Cxxx]` vào câu tương ứng.
3. `python3 -m sma.claims` kiểm tra cấu trúc: mọi tag trong kịch bản đều có trong ledger và ngược lại, cột bắt buộc có đủ, nhãn hợp lệ, nguồn tồn tại, mọi phép tính `DERIVED` khớp lại (`tools/check_numbers.py` nếu có).
4. **Independent scientific review**: một agent hay lượt tách biệt, không phải người viết. Kiểm tra phương trình, đơn vị, niên đại, cách diễn giải, chỗ thiếu từ hạn định. Có quyền REJECT.
5. **Pedagogy review**: kiểm tra khả năng hiểu với người học L0.
6. Người viết sửa, reviewer xác nhận, cột `reviewer_status` chuyển sang `APPROVED` hoặc `REVISED`.
7. Một người thật nghe pilot và duyệt trước mọi phát hành ra ngoài.

## 5. Sửa lỗi sau phát hành

Ghi vào `revision_history` trong `metadata.json`: ngày, mức độ (CRITICAL / MAJOR / MINOR), claim bị ảnh hưởng, phiên bản bị ảnh hưởng, và có phải rút hay xuất lại MP3 không.

## 6. Điểm dừng cứng (fail closed)

Không tổng hợp audio khi gặp một trong các trường hợp:
- Claim trọng yếu không có nguồn.
- Hai nguồn uy tín mâu thuẫn mà chưa giải quyết.
- Thông tin y tế sai có thể gây hại.
- Công thức sai đơn vị.
- Có nội dung được bảo hộ của bên thứ ba bị sao chép.
- Không rõ giấy phép giọng đọc hay nhạc.
- Còn claim ở trạng thái `PENDING` hoặc `REJECTED`.

Nếu không xác minh được một claim trọng yếu thì **sửa hoặc bỏ nó**, không giữ lại với hy vọng là đúng.
