# TTS benchmark — Vietnamese local engines on Android ARM64 (M3)

Ngày đo: 2026-10-14. Thiết bị: xem `ENVIRONMENT_AUDIT.md` (Snapdragon 8 Gen 3, 8 lõi, Ubuntu 24.04 proot, không root).
Công cụ: `tools/bench_tts.py`, chạy **từng engine một, không đồng thời**, nghỉ 30 s giữa hai engine; lấy mẫu RSS, CPU-time, nhiệt CPU và nhiệt pin mỗi 0,5 s.
Dữ liệu thô: `~/.cache/sma-bench/bench_results.json`, các file `asr.json` (không commit vì chứa WAV/đường dẫn cục bộ).

## Bộ thử (giống hệt nhau cho mọi engine)

`production/benchmarks/bench_items.json`, 22 mục:
- `p1_raw`: đoạn văn khoảng 55 giây, để nguyên số, đơn vị, tên riêng (Newton, Einstein, Schrödinger, electron, MeV, E=mc^2, DNA, 150 triệu km, 300.000 km/s, không-thời gian, chân trời sự kiện).
- `p2_norm`: cùng đoạn văn, đã chuẩn hóa phát âm (201 từ).
- 20 câu thử thuật ngữ: 10 thuật ngữ bắt buộc của nhiệm vụ, mỗi thuật ngữ ở dạng gốc và dạng phiên âm.

## Ứng viên và giấy phép

| Engine | Model | Giấy phép (đã kiểm) | Offline | ARM64 |
|---|---|---|---|---|
| Piper vais1000-medium | `vits-piper-vi_VN-vais1000-medium` qua sherpa-onnx 1.13.8 | Dataset VAIS-1000 **CC BY 4.0** (MODEL_CARD) | Có | Có (wheel aarch64 chính thức) |
| VieNeu-TTS v3 Nano | `pnnbao-ump/VieNeu-TTS-v3-Nano`, 48M tham số, flow-matching | **Apache-2.0**; trạng thái **preview** | Có (sau khi tải model) | Có (onnxruntime 1.31) |
| VieNeu-TTS v3 Turbo int8 | `pnnbao-ump/VieNeu-TTS-v3-Turbo`, `onnx_int8` | **Apache-2.0**, áp dụng cả giọng preset; tài liệu cho phép dùng thương mại | Có | Chạy được, nhưng chậm |
| VieNeu-TTS v3 Turbo fp32 | như trên, `onnx_update` | **Apache-2.0** | Có | Có, cần sửa lỗi symlink (bên dưới) |
| *Loại từ đầu* | Piper `vi_VN-25hours_single` (dataset **License: Unknown**); Piper `vi_VN-vivos` (**CC BY-NC-SA**, cấm thương mại) | — | — | — |

VieNeu mặc định chèn **watermark audio AI**; chúng tôi giữ bật (`watermark: true`) để minh bạch.

## Kết quả đo (22 mục, cùng điều kiện)

| Engine | Load (s) | Audio (s) | Tổng hợp (s) | **RTF** | **RAM đỉnh** | Lõi CPU bận TB | **CPU max** | Pin max | Lỗi |
|---|---|---|---|---|---|---|---|---|---|
| Piper vais1000 | 2,0 | 146,1 | 23,3 | **0,16** | 484 MiB | 3,4 | 52,9°C | 37,5°C | 0 |
| VieNeu Nano | 8,9 | 169,4 | 310,3 | **1,83** | 680 MiB | 2,3 | 51,3°C | 38,0°C | 0 |
| VieNeu Turbo int8 | 29,9 | 163,8 | 1577,1 | **9,63** | 2308 MiB | 5,6 | 50,9°C | 37,6°C | 0 |
| VieNeu Turbo fp32 | 17,1 | 166,0 | 459,6 | **2,77** | 3289 MiB | 6,1 | 64,1°C | 37,6°C | 0 |

RTF = thời gian tổng hợp ÷ thời lượng audio (nhỏ hơn là nhanh hơn). Nhiệt độ đo bằng sensor của SoC; không đo được điện năng tiêu thụ.

Ghi chú:
- Nhà phát triển công bố RTF CPU của Nano là 0,22 và của Turbo là 0,62 (fp32) / 0,37 (int8). Trên thiết bị này **chậm hơn 3–26 lần**. Đường int8 cần lệnh VNNI (x86); ARM có `i8mm`/`asimddp` nhưng onnxruntime không tăng tốc được trong trường hợp này.
- Turbo fp32 bị lỗi khởi tạo `External data path escapes model directory` (onnxruntime 1.31 + symlink trong cache HuggingFace). **Cách khắc phục:** `cp -L` thư mục `onnx_update` sang `~/.cache/sma-models/vieneu-turbo-fp32-onnx/` rồi truyền `onnx_dir`.
- Không có sự cố nhiệt: CPU tối đa 64°C, pin tối đa 38°C. Điện thoại vẫn chạy song song các agent khác.

## Độ dễ hiểu: ASR làm kiểm tra phụ (không thay tai người)

ASR: `sherpa-onnx-zipformer-vi-int8-2025-04-20`. CER thấp gợi ý lời dễ hiểu. CER cao chỉ có nghĩa là "cần nghe trước", không chứng minh phát âm sai.

| Engine | CER `p2_norm` | CER `p1_raw` | CER trung vị 20 câu thuật ngữ | Tốc độ đọc |
|---|---|---|---|---|
| Piper | 6,4% | 11,5% | 26,6% | 4,45 âm tiết/s |
| Nano | **4,3%** | **7,3%** | **17,6%** | 3,83 âm tiết/s |
| Turbo int8 | 5,6% | 8,0% | 18,8% | 4,17 âm tiết/s |
| Turbo fp32 | 6,0% | 8,8% | 19,9% | 4,16 âm tiết/s |

Quan sát:
- Piper: ASR nghe "hai mươi" thành "hay mười", và "không thời gian" thành "khung/khâu thời gian".
- Các engine VieNeu tự chuẩn hóa được "300.000 km/s", "DNA", "không-thời gian".
- **Câu thuật ngữ:**
  - "E bằng em nhân xê bình phương" (dạng phiên âm) tốt ở mọi engine (CER 6–13%), còn dạng gốc `E=mc^2` bị đọc thành "mũ hai".
  - "chân trời sự kiện" và "km/s": 0% CER trên VieNeu.
  - "MeV" và "electron" kém ở mọi engine, kể cả dạng phiên âm. Trong kịch bản tương lai nên viết thành lời ("triệu e-léc-trôn vôn", hoặc dùng "điện tử" khi phù hợp), và phải nghe thử.
  - Tên riêng (Newton, Einstein, Schrödinger): ASR ghi theo chính tả tiếng Anh, nên **CER không phản ánh phát âm**. Với Turbo, "Einstein" để nguyên được ASR nhận là "Anh Stein", còn "Anh-xtanh" lại thành "Anh Axing". **Cần nghe bằng tai** để chọn dạng phiên âm.

## Lựa chọn

| Vai trò | Engine | Lý do |
|---|---|---|
| **Primary** | VieNeu Turbo fp32, giọng preset "Hải Đăng" (nam, Bắc, tự nhiên; mặc định của SDK) | Chất lượng cao nhất theo nhà phát triển, 48 kHz, độ dễ hiểu (ASR) tương đương Nano, tài nguyên chấp nhận được (tập 11 phút khoảng 30 phút render, RAM 3,3 GiB, ≤ 64°C) |
| **Fallback** | VieNeu Nano, giọng "Minh Quân" | Nhẹ (680 MiB), mát, CER thấp nhất. Nhà phát triển nói chất lượng thấp hơn Turbo rõ rệt và đây là bản preview |
| Khẩn cấp | Piper vais1000 | Nhanh gấp 17 lần Turbo fp32; giấy phép dataset rõ ràng; ASR cho thấy lỗi thanh điệu |
| Loại | Turbo int8 | RTF 9,6 trên CPU này |

**Quyết định này chưa có kiểm nghe của người thật.** File so sánh 4 engine (cùng đoạn văn và cùng 10 câu thuật ngữ) nằm ở
`/storage/emulated/0/Download/Science_Audio_VN/00_Science_Media_Academy/tts_samples/sample_<engine>.mp3` (kèm `SHA256SUMS.txt`). Người dùng nên nghe và xác nhận lựa chọn.

## Quyền giọng đọc (cần người dùng quyết định trước khi phát hành)

Giọng preset của VieNeu được phân phối theo Apache-2.0, và tài liệu cho phép dùng thương mại. Tuy vậy, vài preset mang tên giống người thật (ví dụ "Phạm Tuyên", "Xuân Vĩnh"), còn nguồn gốc dữ liệu giọng thì chúng tôi **không xác minh được**. Pilot dùng "Hải Đăng" (tên chung, preset mặc định). **Không clone giọng nào.** Trước khi phát hành công khai, người dùng cần xác nhận lựa chọn giọng.
