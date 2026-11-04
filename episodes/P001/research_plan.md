# Research plan — P001 "Biết rằng mình không biết"

Trạng thái 2026-11-04: **chưa cache nguồn nào**. Phiên cloud này bị chính sách mạng chặn mọi trang nguồn bên dưới (proxy trả 403 cho
plato.stanford.edu, iep.utm.edu, ctext.org, gutenberg.org, eutils.ncbi.nlm.nih.gov…). Vì vậy chưa có claim hay kịch bản.
Mọi tiêu đề, URL, vị trí dưới đây là **ứng viên viết từ trí nhớ của agent**, phải kiểm tra khi cache (bài học 20): sai thì sửa, không có thì bỏ.

## Bước 0: mở đường lấy nguồn (một trong ba cách)
1. **Mở mạng cho môi trường cloud**: thêm các host sau vào *Allowed domains* trong cài đặt môi trường
   (https://code.claude.com/docs/en/cloud-environments#network-access):
   `plato.stanford.edu`, `iep.utm.edu`, `ctext.org`, `suttacentral.net`, `www.perseus.tufts.edu`, `www.gutenberg.org`,
   `www.accesstoinsight.org`, `eutils.ncbi.nlm.nih.gov`, `api.crossref.org`, `philpapers.org`, `vi.wikisource.org`.
2. **Chạy trên điện thoại** (Termux, nơi `tools/research.py` đã chạy được với PubMed/Smithsonian).
3. **Qua Google Drive**: người dùng lưu trang (in ra PDF hoặc chép văn bản) vào `MyDrive/Science_Media_Academy/philosophy_sources/`;
   agent đọc qua Drive connector, lưu file text vào scratchpad, rồi `python3 tools/research.py add <tên> <file> <url gốc>`.

## Bước 1: cache
```bash
python3 tools/research.py web sep_socrates https://plato.stanford.edu/entries/socrates/
python3 tools/research.py web sep_confucius https://plato.stanford.edu/entries/confucius/
python3 tools/research.py web sep_buddha https://plato.stanford.edu/entries/buddha/
python3 tools/research.py web iep_socrates https://iep.utm.edu/socrates/
python3 tools/research.py web ctext_analects_2 https://ctext.org/analects/wei-zheng
python3 tools/research.py web sc_an3_65 https://suttacentral.net/an3.65/en/sujato
python3 tools/research.py web ati_bodhi_kalama https://www.accesstoinsight.org/lib/authors/bodhi/bps-essay_09.html
python3 tools/research.py pm 10626367          # Kruger & Dunning 1999 (kiểm tra PMID)
python3 tools/research.py pm-search "intellectual humility[ti] AND Porter[au]"
```
SuttaCentral render bằng JavaScript: nếu `web` chỉ lấy được khung trang, dùng API JSON của SuttaCentral hoặc bản Access to Insight (Thanissaro) và ghi rõ dịch giả.

## Bước 2: nguồn ứng viên (mã PS đề xuất; ghi vào `research/PHILOSOPHY_SOURCE_REGISTER.md` khi đã đọc)

| Mã đề xuất | Nguồn ứng viên | Dùng cho | Cần kiểm tra |
|---|---|---|---|
| PS001 | Plato, *Apology* (*Biện hộ*) 20e–23b, bản dịch H. N. Fowler (Perseus) hoặc B. Jowett (Gutenberg) | Mục 5–6: lời sấm, cuộc tra hỏi, câu then chốt quanh 21d | Số Stephanus chính xác của từng câu; tên và năm bản dịch |
| PS002 | SEP, "Socrates" (Debra Nails) | Vấn đề Socrates; niên đại; cách đọc sự thiếu hiểu biết | Tác giả, ngày sửa đổi |
| PS003 | IEP, "Socrates" | Đối chiếu thứ hai cho mục 6–7 | Tác giả |
| PS004 | *Luận Ngữ* 2.17 (Vi chính), ctext.org, nguyên văn + bản dịch James Legge | Mục 8 | Số chương; nguyên văn; tên Tử Lộ (由) |
| PS005 | SEP, "Confucius" | Bối cảnh Khổng Tử; *Luận Ngữ* là sách do học trò biên soạn | Tác giả, ngày sửa đổi |
| PS006 | Một bản dịch *Luận Ngữ* tiếng Việt đã xuất bản (ứng viên: bản trên vi.wikisource hoặc bản in có tên dịch giả) | Mục 8: đối chiếu bản dịch Việt | **Chưa xác định**; bỏ nếu không tìm được bản có tên dịch giả |
| PS007 | Kinh Kālāma (*Kesamutti Sutta*), AN 3.65, bản dịch Bhikkhu Sujato (SuttaCentral) | Mục 9: danh sách căn cứ, tiêu chí | Danh sách đầy đủ; có "lý lẽ/suy luận" (*takka*) trong danh sách hay không |
| PS008 | SEP, "Buddha" | Niên đại Đức Phật và tranh luận; kinh do truyền khẩu rồi mới viết | Tác giả |
| PS009 | Bhikkhu Bodhi, "A Look at the Kalama Sutta" (Access to Insight) | Mục 9: cách đọc sai phổ biến và bối cảnh bài kinh | URL, năm |
| PS010 | Liddell–Scott–Jones, mục φιλοσοφία (Perseus) hoặc một mục SEP/IEP về định nghĩa triết học | Mục 2: nghĩa gốc của *philosophia* | Có hay bỏ |
| PS011 | Nguồn học thuật về Nishi Amane và chữ 哲學 (ứng viên: SEP "Japanese Philosophy") | Mục 2: nguồn gốc từ Hán "triết học" | **Chỉ giữ nếu xác minh được**; nếu không, bỏ cả ý |
| PS012 | Porter T. và cộng sự, tổng quan về khiêm tốn trí tuệ (ứng viên: *Nature Reviews Psychology* 2022) | Mục 12 (tùy chọn) | Tác giả, năm, tạp chí |
| PS013 | Fine G. 2008, "Does Socrates claim to know that he knows nothing?", *Oxford Studies in Ancient Philosophy* | Mục 6: phản biện cách đọc "biết là không biết gì" | Có tồn tại đúng tiêu đề; đọc được phần nào |
| PS014 | Kruger J., Dunning D. 1999, *J Pers Soc Psychol* (PMID ứng viên 10626367) | Mục 12 (tùy chọn): nghiên cứu gốc | PMID, abstract |
| PS015 | Một phản biện thống kê về Dunning–Kruger (ứng viên: Gignac & Zajenkowski 2020, *Intelligence*) | Mục 12 (tùy chọn) | Tác giả, năm, nội dung abstract |
| PS016 | Leary M. R. và cộng sự 2017, thang đo khiêm tốn trí tuệ (*Pers Soc Psychol Bull*) | Mục 12 (tùy chọn) | Tác giả, năm |

Mục tiêu 25–35 nguồn (bible): sau khi cache 16 ứng viên trên, tìm thêm (a) một bản dịch *Biện hộ* thứ hai để đối chiếu câu 21d, (b) một nghiên cứu
về *Luận Ngữ* 2.17 hoặc chữ 知, (c) một học giả Phật học thứ hai về Kinh Kālāma, (d) Xenophon *Apology* cho vấn đề Socrates,
(e) một nguồn tiếng Việt có bình duyệt về giảng dạy triết học hoặc về Tam giáo (nối P032).

## Bước 3: sau khi cache
`quote` từng câu → ghi PS vào register → `claims.csv` (12 cột, xem `src/sma/claims.py`) → `script.md` v0.1 có tag `[P001-Cxx]` → `python3 -m sma.claims episodes/P001`
→ `tools/sources_build.py` (kiểm tra công cụ nhận mã PS; nếu không, viết `sources.md` tay) → `tools/names_add.py` → review độc lập
(`production/REVIEW_PROMPT.md` + năm câu hỏi riêng trong bible) **song song** với pre-render Colab → vòng xác nhận → audio → QA.
