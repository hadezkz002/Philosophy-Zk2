# Agent handover — Philosophy-Zk2 ("Hành Trình Tư Tưởng")

Đọc theo thứ tự: `README.md` → `curriculum/PHILOSOPHY_SERIES_BIBLE.md` → `.agent-state/NEXT_ACTION.md` → `production/EPISODE_PLAYBOOK.md`
(viết cho series lịch sử của dự án gốc; ghi chú đầu file nói cách đọc cho repo này) → tài liệu của tập đang làm.
Repo: `hadezkz002/Philosophy-Zk2` (**public**: mọi thứ push lên đều công khai). Dự án gốc: `hadezkz002/science-media-academy` (private).

## Vai trò

| Vai trò | Việc | Ràng buộc |
|---|---|---|
| Research | Cache nguồn (`tools/research.py web|add|pm`), ghi `research/PHILOSOPHY_SOURCE_REGISTER.md` (ID `PS`, URL, bản dịch, **vị trí chuẩn**) | Không trích điều bản cache không có; không dùng trang danh ngôn |
| Scriptwriter | `script.md` gốc, gắn `[PNNN-Cxx]` cho mọi claim | Tách ba tầng văn bản / học giả / người kể; không tự tuyên bố đã qua kiểm định |
| Reviewer | Phản biện độc lập theo `production/REVIEW_PROMPT.md`; **duy nhất** được sửa `reviewer_status`/`reviewer_note` | Lượt hoặc agent tách biệt với người viết; có quyền REJECT |
| Audio | `sma.produce`, Colab, lexicon | Không render bản chính khi cổng claim fail |
| QA / Integration | `qa_full.md`, metadata, git | Không commit audio/model/venv/token |

## Quy trình tập mới
1. Chọn tập trong bản đồ mùa (bible) và `topic_id` trong `curriculum/curriculum.json`; tạo `episodes/PNNN/brief.md`, `outline.md`, `research_plan.md`, `metadata.json`.
2. Research → register → `claims.csv` (PENDING) → `script.md` → `python3 -m sma.claims episodes/PNNN` → `tools/sources_build.py` → `tools/names_add.py`.
3. Review độc lập **song song** với pre-render Colab → sửa (tự kiểm lại mọi trích dẫn) → vòng xác nhận → `sma.claims --release`.
4. Render các chunk đã đổi → `tools/run_episode.sh episodes/PNNN` → QA 9/9 → `qa_full.md` → commit → PR. **Người dùng nghe duyệt** trước mọi phát hành.

## Colab và Google Drive
- Drive của người dùng có `MyDrive/Science_Media_Academy/` với `colab_jobs/` (job render) và `philosophy_sources/` (văn bản nguồn người dùng bỏ vào).
- Không có `colabjob` (phiên cloud): `tools/colab_render.py episodes/PNNN --bundle <dir>` → tải 3 file lên `colab_jobs/<job>/` qua Drive connector →
  người dùng chạy notebook `SMA_Drive_Render.ipynb` (bản sao trên Drive cùng thư mục, hoặc `tools/colab/`) trên GPU T4 → `--ingest <sma_out.tar>`.
  Tải kết quả của cả tập qua connector có thể quá lớn: khi đó chia job (`--only`, `--limit`) hoặc tải bằng điện thoại.
- Nguồn bị mạng chặn: đọc file trong `philosophy_sources/` bằng connector → `tools/research.py add <tên> <file> <url gốc>`; register ghi rõ nguồn gốc file.
- Không đụng các file Drive khác của người dùng (thư mục nhạc, notebook tải nhạc).

## Ràng buộc bất biến
1. Không xóa hay ghi đè dữ liệu người dùng; MP3 hoàn chỉnh vào `Download/Science_Audio_VN/00_Science_Media_Academy/<ID>/` trên điện thoại (`run_episode.sh`).
2. Không API trả phí, không đăng audio công khai, không clone giọng người thật.
3. Không chạy hai model TTS cùng lúc.
4. Không commit MP3/WAV/FLAC, model, venv, token. Repo là public: kiểm tra `git diff --name-only` trước mỗi push.
5. Báo cáo trung thực: PARTIAL khi thiếu điều kiện; không bịa nguồn, trích dẫn hay vị trí đoạn.
6. Chủ đề nhạy cảm (tôn giáo, chính trị, cái chết, tự sát): theo nguyên tắc 8–10 của bible.

## Bẫy kỹ thuật đã gặp (từ dự án gốc)
- `hf-xet` treo trong proot: tải model với `HF_HUB_DISABLE_XET=1`.
- onnxruntime 1.31 từ chối file `.data` qua symlink của HF cache: Turbo fp32 cần bản copy thật (`cp -L`) và tham số `onnx_dir`.
- Chuỗi `<!-- -->` viết nguyên văn **bên trong** một khối chú thích sẽ đóng khối sớm; `sma.produce plan` fail-closed khi thấy markup trong lời đọc.
- ASR ghi tên riêng nước ngoài theo chính tả tiếng Anh: CER của tên riêng không phản ánh phát âm, phải nghe bằng tai.
- Mạng phiên cloud có thể chặn trang nguồn (SEP, IEP, ctext, SuttaCentral, PubMed…): mở trong cài đặt môi trường, hoặc dùng điện thoại, hoặc Drive.
