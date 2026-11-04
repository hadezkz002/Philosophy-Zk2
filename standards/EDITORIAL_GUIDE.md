# Vietnamese science editorial guide v1.0

**Trạng thái:** v1.0 (2026-10-14), nâng cấp từ v0.1. Thay đổi so với v0.1: xem *Changelog* ở cuối.
**Định hướng:** Scientific Storytelling + First-Principles Reasoning + Evidence-Based Education.
Căn cứ nghiên cứu: `research/NARRATIVE_PATTERNS.md`, `research/SCIENTIFIC_REASONING_PATTERNS.md`, `research/AUDIO_ADAPTATION_GUIDE.md`.

## 1. Lời hứa với người học

**Không chỉ nói điều gì đúng. Giải thích vì sao ta biết nó đúng, bằng chứng nào ủng hộ, và ta chưa biết điều gì.**

Mỗi bài phải giúp người nghe trả lời được ba câu hỏi:
1. **Điều gì đang xảy ra?** (hiện tượng, mô tả)
2. **Vì sao nó xảy ra?** (cơ chế, mô hình)
3. **Làm sao chúng ta biết điều đó?** (bằng chứng, phép đo, suy luận và giới hạn)

Người nghe mục tiêu là người Việt tò mò, bắt đầu từ con số 0. Giọng văn chín chắn, chính xác, gần gũi, thỉnh thoảng dí dỏm. Không la hét, không làm người nghe xấu hổ, không hứa hẹn thần kỳ, không chắc chắn khi thiếu căn cứ, không "tin nóng" giả tạo.

## 2. Kiến trúc tường thuật khuyến nghị (tham khảo, không phải khuôn cứng)

| # | Nhịp | Mục đích | Ghi chú audio |
|---|---|---|---|
| 1 | **Hook** | Câu hỏi gây tò mò, quan sát được hoặc là thí nghiệm tưởng tượng rõ ràng | Không quá 40–60 giây. Hook không được hứa nhiều hơn phần thân giải quyết được (xem rủi ro R1 trong SCIENTIFIC_REASONING_PATTERNS) |
| 2 | **Context** | Bối cảnh đời thực hoặc lịch sử khám phá | Lịch sử phải có nguồn. Giai thoại chưa xác minh phải nói rõ là giai thoại |
| 3 | **Intuition** | Gọi tên trực giác hoặc ngộ nhận phổ biến một cách tôn trọng | "Nhiều người sẽ đoán rằng…" |
| 4 | **Mental model** | Thực thể, quan hệ nhân quả, giả định. Định nghĩa thuật ngữ trước khi dùng | Tối đa 3 khái niệm nền mới mỗi tập |
| 5 | **Reasoning** | Lập luận từng bước, cho người nghe dự đoán trước | Ngắt bằng câu hỏi: "Bạn thử đoán xem…" |
| 6 | **Evidence** | Ai đo, đo gì, bằng phương pháp nào. Có thể là chứng minh toán học | Mỗi đoạn tối đa 1–2 con số |
| 7 | **Limitations** | Giới hạn của mô hình, của phép so sánh, những điều chưa biết | Bắt buộc, không được bỏ |
| 8 | **Thought experiment** | Áp mô hình vào tình huống mới để kiểm tra hiểu biết | Đánh dấu FICTION nếu tình huống bất khả |
| 9 | **Recap** | Một câu cốt lõi và 1–2 câu hỏi tự kiểm tra | |
| 10 | **Next question** | Nối sang chủ đề kế tiếp trong lộ trình (LEARNING_MAP) | |

Đơn vị lập luận ưu tiên: **Claim → Mechanism → Evidence → Caveat → Implication.** Lời kể có thể đảo thứ tự để tạo hồi hộp, nhưng bản kịch bản cuối phải có đủ năm thành phần.

## 3. Quy tắc lập luận

- Mỗi tập 8–15 phút chỉ có một câu hỏi khoa học chính.
- Câu chuyện, giai thoại, phép so sánh, hình minh họa hay phần dựng lại bằng AI **không phải là bằng chứng**.
- Mọi con số phải có đơn vị, điều kiện vật lý, số chữ số có nghĩa hợp lý và nguồn. Làm tròn phải nói "khoảng".
- Tách tương quan khỏi nhân quả. Không biến liên hệ thống kê thành điều chắc chắn.
- Với nghiên cứu còn tranh cãi: trình bày bằng chứng chính thống mạnh nhất, nêu quan điểm thiểu số rõ ràng nhưng không cân bằng giả tạo.
- Y học: không suy ra khuyến nghị chẩn đoán hay điều trị từ cơ chế giáo dục.
- Nhà khoa học nổi tiếng cũng có thể sai. Uy tín không thay được dữ liệu.
- Không đơn giản hóa đến mức sai. Nếu cần đơn giản hóa, nói rõ "đây là phiên bản rút gọn, đúng trong điều kiện…".
- Phân biệt rõ mô hình tưởng tượng với hiện tượng quan sát được.

## 4. Nhãn nội dung (đồng bộ với FACT_CHECK_POLICY và claims.csv)

| Nhãn (claims.csv) | Tên trong nhiệm vụ | Ý nghĩa |
|---|---|---|
| `ESTABLISHED` | Established science | Mô hình được hỗ trợ mạnh, đồng thuận rộng (không phải chân lý tuyệt đối) |
| `OBSERVED` | Observational evidence | Kết quả đo hoặc quan sát có phương pháp |
| `DERIVED` | Mathematical derivation | Suy ra bằng phép tính từ đại lượng đã có nguồn |
| `HYPOTHESIS` | Hypothesis | Giả thuyết kiểm chứng được, chưa được xác nhận |
| `SPECULATION` | Speculation | Ý tưởng có thể chưa kiểm chứng được |
| `ANALOGY` | Analogy | Công cụ giảng dạy, không đồng nhất về vật lý |
| `FICTION` | Fictional thought experiment | Kịch bản tưởng tượng, phải nói rõ với người nghe |
| `HISTORICAL` | (bổ sung) | Sự kiện lịch sử, cần nguồn sử liệu hoặc học thuật |
| `DEFINITION` | (bổ sung) | Định nghĩa hoặc quy ước (ví dụ giá trị chính xác của c theo SI) |

Không được biến `HYPOTHESIS`/`SPECULATION` thành sự thật đã chứng minh. Trong lời đọc phải có từ báo hiệu tương ứng: "giả thuyết cho rằng", "một số nhà vật lý suy đoán", "hãy tưởng tượng".

## 5. Chuyển thể cho audio (tóm tắt, chi tiết ở AUDIO_ADAPTATION_GUIDE)

- Mọi hình ảnh cần cho lập luận phải được nói thành lời: "hãy hình dung…".
- Công thức: nói **ý nghĩa** trước, ký hiệu sau. Ví dụ: "năng lượng bằng khối lượng nhân bình phương tốc độ ánh sáng, viết gọn là E bằng m c bình phương".
- Sau mỗi lần đổi thang đo, có một câu neo vị trí ngắn. Sau mỗi phần lớn, tóm tắt một câu.
- Câu ngắn, mỗi đoạn một ý. Không đọc liền một danh sách số liệu.
- Duy trì từ điển phát âm (`episodes/<id>/pronunciation.json`) cho tên riêng, đơn vị, viết tắt, ký hiệu.
- Nhạc (nếu có) không được che lời. Mặc định không dùng nhạc nền liên tục.
- Không bắt chước giọng, câu cửa miệng, giai điệu hay nhận diện của các kênh tham khảo.

## 6. Rubric biên tập 100 điểm

| Tiêu chí | Điểm | Câu hỏi kiểm tra |
|---|---|---|
| Scientific accuracy | **35** | Mọi claim trọng yếu đúng, có nguồn trong claim ledger, đúng nhãn, đúng đơn vị và phép tính? |
| Reasoning quality | **20** | Có chuỗi nhân quả từ nguyên lý đầu tiên? Giả định có được nêu rõ? Có tách giả thuyết khỏi thực nghiệm? |
| Beginner accessibility | **15** | Người học L0 hiểu được không? Thuật ngữ được định nghĩa chưa? Có quá 3 khái niệm mới? |
| Narrative quality | **10** | Hook, độ căng, nhịp, phần giải quyết, câu hỏi kế tiếp |
| Audio suitability | **10** | Nói được thành lời không cần hình? Câu dễ đọc? Phát âm thuật ngữ đã xử lý? |
| Originality & intellectual honesty | **10** | Văn bản tự viết? Nêu giới hạn? Không phóng đại? Không sao chép kênh tham khảo? |

**Ngưỡng duyệt:** từ 85 điểm trở lên **và** không có lỗi khoa học CRITICAL hay MAJOR chưa sửa. Lỗi khoa học nghiêm trọng không thể bù bằng điểm kể chuyện: có một lỗi CRITICAL là **REJECT**, bất kể tổng điểm. Reviewer phải tự phản biện claim trung tâm và ít nhất 2 claim định lượng hoặc lịch sử.

Phân loại mức độ lỗi: **CRITICAL**: sai cơ chế trung tâm, sai số liệu làm đổi kết luận, giả thuyết bị trình bày như sự thật. **MAJOR**: thiếu giới hạn quan trọng, số liệu sai nhưng không đổi kết luận, nhãn sai. **MINOR**: diễn đạt, nhịp, phát âm.

## 7. Quy trình sản xuất

```
Research → Scriptwriting → Independent Review (science + pedagogy) → Revision → Approval → Audio Production → Audio QA → Human listening approval → (Release, cần duyệt riêng)
```

- Người viết kịch bản **không được** tự tuyên bố kịch bản của mình đã qua kiểm định độc lập.
- Reviewer phải là một lượt hoặc agent tách biệt, có quyền REJECT. Kết quả ghi vào `episodes/<id>/review.md`.
- Không tổng hợp audio đầy đủ khi kịch bản còn lỗi CRITICAL hay MAJOR.
- Mọi sửa đổi sau khi duyệt phải tăng `script_version` và ghi vào `revision_history` trong metadata.

## 8. Anti-patterns

- "Các nhà khoa học đã chứng minh…" mà không nêu nghiên cứu và thiết kế cụ thể.
- Dùng một video YouTube hay ảnh chụp màn hình làm bằng chứng khoa học.
- Tiêu đề hay hook hứa "bằng chứng" trong khi thân bài chỉ có lý thuyết.
- Mô tả lỗ sâu đục, du hành thời gian như đã chế tạo hoặc quan sát được.
- Bỏ qua chỗ mà phép so sánh hay hoạt hình không còn đúng.
- Sao chép hoạt hình, văn bản, đồ họa hay giọng đọc của kênh khác.
- Đọc bằng AI hàng loạt mà không qua QA phát âm và bằng chứng.

## Changelog

- **v1.0 (2026-10-14):** thêm ba câu hỏi cốt lõi; kiến trúc 10 nhịp; bảng nhãn đồng bộ claims.csv (thêm HISTORICAL, DEFINITION); rubric với tên tiêu chí theo nhiệm vụ, kèm câu hỏi kiểm tra; phân loại mức độ lỗi; quy trình sản xuất có bước duyệt nghe.
- v0.1 (2026-10-14): bản baseline.
