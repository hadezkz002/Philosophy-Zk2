# Series bible — "Hành Trình Tư Tưởng" (tên tạm)

Trạng thái: **PLAN**. Ngày: 2026-11-04. Repo: `hadezkz002/Philosophy-Zk2` (dự án độc lập).
Dự án tách ra từ Science Media Academy (`hadezkz002/science-media-academy`, commit `c79937b`), nơi có series lịch sử "Hành Trình Nhân Loại".
Repo này mang theo bản sao hạ tầng cần thiết (chuẩn biên tập, cổng claim, pipeline TTS, đường render Colab) và chạy được một mình.
Tập: `episodes/PNNN/`; sổ nguồn: `research/PHILOSOPHY_SOURCE_REGISTER.md` (mã `PS`); chương trình: miền `PHIL` trong `curriculum/curriculum.json`.
Tập triết học có thể **nhắc** tập lịch sử của dự án kia để đặt bối cảnh (ví dụ "H019 Thương và Chu"), nhưng không phụ thuộc vào file của nó.

## Tiền đề

Một chuyến đi bằng tiếng Việt qua những câu hỏi lớn mà con người ở nhiều nơi đã đặt ra: *Ta biết được gì? Cái gì là thật? Nên sống thế nào?
Sống cùng nhau ra sao? Đời có ý nghĩa gì?* Người nghe bắt đầu từ con số 0. Mỗi tập trả lời bốn câu hỏi:

1. **Câu hỏi là gì**, và vì sao nó khó hơn vẻ ngoài?
2. **Văn bản nói gì**: đọc chính nguyên tác (qua bản dịch có tên), có vị trí đoạn trích.
3. **Học giả hiểu thế nào**: các cách đọc cạnh tranh, ghi rõ ai nói.
4. **Lập luận có đứng vững không**: tái dựng thành tiền đề và kết luận, rồi đưa phản biện mạnh nhất.

Mục tiêu không phải dạy người nghe *tin gì*, mà dạy *cách nghĩ*: tách tiền đề khỏi kết luận, tìm phản ví dụ, và biết mình đang chưa biết gì.
Thời lượng do nội dung quyết định (bài học 15 của playbook). Mục tiêu nội dung khoảng 4.500–6.500 từ mỗi tập.

## Nguyên tắc (bắt buộc)

1. **Ba tầng tách bạch, không trộn trong một câu:**
   - *Văn bản nói*: "Trong *Biện hộ* (21d), Socrates nói…" (`PRIMARY_TEXT`).
   - *Học giả đọc*: "Theo Vlastos…, còn theo…" (`INTERPRETATION`). Ý của học giả **không** được nói bằng giọng người kể.
   - *Người kể đánh giá*: chỉ khi báo trước bằng lời ("theo ý người kể…") (`NARRATOR_VIEW`), dùng ít, không bao giờ cho câu hỏi đạo đức/chính trị đang tranh cãi.
2. **Trích dẫn nguyên tác có địa chỉ.** Mỗi câu trích ghi: tác phẩm, vị trí chuẩn (số Stephanus cho Plato, số Bekker cho Aristotle,
   chương.tiết cho *Luận Ngữ*, mã kinh cho tạng Pali, v.v.), bản dịch (dịch giả, năm) và nơi lấy bản dịch. Câu tiếng Việt chuyển ngữ từ bản tiếng Anh
   phải ghi "chuyển ngữ của dự án từ bản dịch của X" (`TRANSLATION_NOTE` khi lựa chọn từ ngữ ảnh hưởng tới nghĩa). Có bản dịch tiếng Việt đã xuất bản thì nêu.
3. **Chống trích dẫn giả.** Triết học đầy câu "nổi tiếng" mà nguyên tác không có. Không dùng trang tổng hợp danh ngôn, mạng xã hội hay bản tóm tắt bằng AI làm nguồn.
   Khi một câu phổ biến khác với nguyên tác, đó là một claim riêng (`MISATTRIBUTION`): nói câu phổ biến, đọc nguyên tác, giải thích chỗ khác.
4. **Dựng mạnh trước khi phản bác (steelman).** Trình bày mỗi quan điểm ở dạng mạnh nhất mà người theo nó chấp nhận, rồi mới đưa phản biện (`OBJECTION`) có nguồn.
   Không "cân bằng giả": nếu giới học thuật gần như đồng thuận về một cách đọc văn bản, nói vậy.
5. **Tái dựng lập luận phải minh bạch.** Dạng "Tiền đề 1… Tiền đề 2… Vậy…" là `ARGUMENT_RECONSTRUCTION`: ghi nó dựa trên đoạn nào và có theo một học giả nào không.
   Không gán cho triết gia một tiền đề mà văn bản không có, trừ khi nói rõ "tiền đề ngầm, do người kể bổ sung".
6. **Toàn cầu, không lấy châu Âu làm mặc định.** Mỗi mùa có ít nhất ba truyền thống trong số: Hy Lạp–La Mã và châu Âu, Trung Hoa, Ấn Độ (Bà La Môn, Phật giáo,
   Kỳ Na giáo, Cārvāka), thế giới Hồi giáo, châu Phi, Việt Nam và Đông Nam Á, châu Mỹ bản địa (khi có nguồn tốt). Tránh hai khuôn sáo: "triết học = phương Tây",
   và "phương Đông thì huyền bí, phương Tây thì lý trí". Có tiếng nói của phụ nữ khi có văn bản (Ban Chiêu, Elisabeth xứ Bohemia, Mary Wollstonecraft…).
7. **Bối cảnh lịch sử có kỷ luật.** Niên đại triết gia cổ thường không chắc (Đức Phật, Lão Tử…): luôn nói khoảng và nói còn tranh luận. Tách tiểu sử truyền thuyết
   (`LATER_HISTORIOGRAPHY`) khỏi văn bản. Khi cần bối cảnh, nhắc tập lịch sử tương ứng (ví dụ H019 Thương và Chu cho Khổng Tử, H024 Tôn giáo lan truyền).
8. **Tôn giáo và tín ngưỡng:** trình bày như truyền thống tư tưởng với sự tôn trọng; không phán xét đức tin đúng hay sai; tách lập luận triết học khỏi giáo lý khi cần,
   và nói rõ khi một văn bản là kinh điển tôn giáo.
9. **Chính trị đương đại:** không cổ vũ đảng phái, không gán triết gia cổ vào phe phái ngày nay. Ví dụ đương đại phải trung tính và có nguồn.
10. **Sức khỏe tinh thần:** các tập về cái chết, khổ đau, ý nghĩa, Camus và tự sát theo hướng dẫn đưa tin an toàn: không mô tả phương thức, không lãng mạn hóa,
    có thông tin tìm hỗ trợ. Khắc kỷ hay thiền **không** được giới thiệu như liệu pháp chữa bệnh; nếu nhắc tới nghiên cứu tâm lý (ví dụ CBT), phải có nguồn bình duyệt.
11. **Khi nói về con người thật nghĩ gì** ("đa số người cho rằng…"), dùng dữ liệu triết học thực nghiệm hoặc tâm lý học đã bình duyệt, kèm cảnh báo về cỡ mẫu,
    văn hóa của mẫu và khả năng tái lập. Không trộn khảo sát ý kiến với chứng minh triết học.
12. **Thí nghiệm tư duy** (`THOUGHT_EXPERIMENT`) được báo trước bằng lời ("hãy thử tưởng tượng…"), ghi ai nghĩ ra và trong tác phẩm nào; thí nghiệm do người kể bịa
    thì nói rõ là của người kể.

### Nhãn claim của series (thêm vào `src/sma/claims.py`)

| Nhãn | Dùng khi | Cần nguồn? |
|---|---|---|
| `PRIMARY_TEXT` | Câu trích hoặc tóm tắt sát một đoạn nguyên tác | Có: bản dịch + vị trí chuẩn |
| `TRANSLATION_NOTE` | Lựa chọn dịch thuật ảnh hưởng tới nghĩa (ví dụ *aretē*, 仁 *nhân*, *dukkha*) | Có |
| `INTERPRETATION` | Cách đọc của một học giả hay trường phái | Có, ghi tên |
| `CONTESTED` | Câu hỏi diễn giải hay sử liệu còn tranh luận thực sự | Có, mỗi phía một nguồn |
| `ARGUMENT_RECONSTRUCTION` | Dạng tiền đề–kết luận của một lập luận | Có: đoạn văn bản mà nó dựa vào |
| `OBJECTION` | Phản biện đã được công bố | Có |
| `THOUGHT_EXPERIMENT` | Thí nghiệm tư duy của một tác giả | Có (nếu của người kể: dùng `STORYTELLER_CONJECTURE`) |
| `MISATTRIBUTION` | Câu phổ biến bị gán sai hoặc lệch nguyên tác | Có: nguyên tác + nguồn học thuật nói về sự lệch |
| `NARRATOR_VIEW` | Đánh giá riêng của người kể, đã báo trước | Không (nhưng reviewer xem nó có cần thiết không) |
| `HISTORICAL`, `LATER_HISTORIOGRAPHY`, `ESTABLISHED`, `OBSERVED`, `DEFINITION` | Như các series khác | Có |

Loại bằng chứng (`evidence_type`) thêm: `primary_text` (nguyên tác qua bản dịch có tên), `reference_work` (bách khoa học thuật có bình duyệt như SEP, IEP).

### Thang nguồn

| Bậc | Nguồn | Ghi chú |
|---|---|---|
| 1 | Nguyên tác trong bản dịch học thuật: Perseus (Plato, Aristotle), Chinese Text Project (ctext.org: *Luận Ngữ*, *Mạnh Tử*, *Trang Tử*…), SuttaCentral (tạng Pali, bản dịch Bhikkhu Sujato thuộc phạm vi công cộng), Project Gutenberg, Wikisource | Ghi dịch giả và năm. Bản dịch còn bản quyền: chỉ trích ngắn có ghi công |
| 2 | Stanford Encyclopedia of Philosophy (SEP), Internet Encyclopedia of Philosophy (IEP) | Ghi ngày sửa đổi của mục từ (SEP có "substantive revision") |
| 3 | Bài báo bình duyệt và sách học thuật (PhilPapers, Crossref; PubMed cho triết học thực nghiệm và tâm lý) | Chỉ dùng phần đã đọc được (abstract hoặc bản mở) |
| 4 | Nghiên cứu tiếng Việt có bình duyệt hoặc của viện nghiên cứu (ví dụ Viện Triết học) cho tư tưởng Việt Nam | Ưu tiên khi nói về Đại Việt |
| Cấm | Trang danh ngôn, blog không tác giả, video tóm tắt, bản tóm tắt của AI | |

Mục tiêu 25–35 nguồn mỗi tập: 3–8 đoạn nguyên tác, 4–8 mục SEP/IEP, phần còn lại là nghiên cứu, trong đó có ít nhất một phản biện cho mỗi cách đọc gây chú ý.

## Bản đồ 7 mùa (dự kiến 5 tập mỗi mùa; sẽ điều chỉnh theo nguồn)

| Mùa | Chủ đề | Tập dự kiến (tên tạm) | Truyền thống tối thiểu |
|---|---|---|---|
| I | Học cách hỏi: công cụ của người làm triết | **P001** Biết rằng mình không biết · P002 Một lập luận gồm những gì? (tiền đề, kết luận, hợp lệ và đúng) · P003 Ngụy biện: cái bẫy của lời nói hay · P004 Thí nghiệm tư duy: phòng thí nghiệm trong đầu · P005 Triết học, khoa học và tôn giáo khác nhau ở đâu? | Hy Lạp, Trung Hoa (Mặc gia, Danh gia), Ấn Độ (Nyāya), Phật giáo |
| II | Những người hỏi đầu tiên (khoảng 800–200 TCN) | P006 "Từ thần thoại tới lý lẽ"? Các nhà tư tưởng Hy Lạp đầu tiên · P007 Upanishad, Đức Phật và Mahāvīra · P008 Bách gia chư tử: Khổng, Mặc, Lão, Trang · P009 Plato và Aristotle · P010 "Thời trục" (Axial Age): một khái niệm còn tranh cãi | Hy Lạp, Ấn Độ, Trung Hoa; đối chiếu Ba Tư, Israel cổ |
| III | Ta biết được gì? (nhận thức luận) | P011 Hoài nghi: Pyrrho, Trang Tử và Sextus · P012 al-Ghazālī và Descartes: nghi ngờ tới tận cùng · P013 Hume và vấn đề quy nạp · P014 Biết là gì? Nyāya và bài toán Gettier · P015 Lời chứng: tin người khác khi nào? | Hy Lạp, Trung Hoa, Hồi giáo, châu Âu, Ấn Độ |
| IV | Cái gì là thật? Tâm trí và bản thân | P016 Tâm và thân · P017 Vô ngã và căn tính cá nhân (Phật giáo, Locke, Parfit) · P018 Ý chí tự do · P019 Ý thức: máy có thể nghĩ không? (nối miền AIE) · P020 Thời gian và sự thay đổi (Heraclitus, Nāgārjuna, Augustine) | Ấn Độ, Phật giáo, châu Âu, Trung Hoa |
| V | Nên sống thế nào? (đạo đức) | P021 Đức hạnh: Aristotle và Khổng Tử · P022 Hệ quả: Mặc Tử, Bentham, Mill · P023 Nghĩa vụ và phẩm giá: Kant · P024 Bài toán xe điện và triết học thực nghiệm · P025 Bổn phận với động vật và thiên nhiên (Kỳ Na giáo, Singer, đạo đức môi trường) | Hy Lạp, Trung Hoa, châu Âu, Ấn Độ |
| VI | Sống cùng nhau (chính trị và xã hội) | P026 Bản tính người thiện hay ác? Mạnh Tử và Tuân Tử · P027 Khế ước xã hội: Hobbes, Locke, Rousseau · P028 Ibn Khaldūn và vòng đời của triều đại · P029 Công bằng là gì? Rawls và Nozick · P030 Ubuntu và tư tưởng châu Phi | Trung Hoa, châu Âu, Hồi giáo, châu Phi |
| VII | Ý nghĩa, cái chết và thời của chúng ta | P031 Khắc kỷ: kiểm soát được gì? (Epictetus, Marcus Aurelius; không phải liệu pháp) · P032 Tư tưởng Đại Việt: Tam giáo, Trần Nhân Tông, Nguyễn Trãi, Lê Quý Đôn · P033 Hiện sinh: Kierkegaard, Sartre, Beauvoir, Camus · P034 Karl Popper, Thomas Kuhn: khoa học tiến bộ thế nào? · P035 Đạo đức của trí tuệ nhân tạo | Hy Lạp–La Mã, Việt Nam, châu Âu, toàn cầu |

## Liên kết học tập

- Chủ đề mới trong `curriculum/curriculum.json`, miền `PHIL` (L0–L5): `PHIL-L0-01` (P001) → `PHIL-L1-01` lập luận → `PHIL-L2-01` nhận thức luận
  → `PHIL-L3-01` tâm trí, bản thân, ý chí → `PHIL-L4-01` học thuyết đạo đức và tranh luận học thuật → `PHIL-L5-01` tự đọc nguyên tác và phản biện.
- Tiên quyết ngoài repo (chương trình của Science Media Academy, chỉ ghi trong `external_prerequisites`): `HIST-L0-01` (quan sát và niềm tin), `MATH-L0-01` (bằng chứng và phương pháp khoa học), `BIO-L1-01` (DNA và gen).
- Mỗi tập có 3 mục tiêu lõi. Câu hỏi đánh giá hỏi **làm** chứ không hỏi **nhớ**: tái dựng một lập luận, tìm một phản ví dụ,
  phân biệt câu trích thật với câu gán sai. Rubric 6 điểm như series lịch sử.

## Sản xuất

- Quy trình như `production/EPISODE_PLAYBOOK.md` (viết từ series lịch sử; ví dụ H0xx là của dự án gốc) (research → sổ nguồn `PS` → `claims.csv` → kịch bản có tag `[PNNN-Cxx]` → `sma.claims`
  → review độc lập theo `production/REVIEW_PROMPT.md` **cộng thêm** các câu hỏi riêng cho triết học dưới đây → vòng xác nhận → audio → QA).
- Câu hỏi thêm cho reviewer triết học: (a) câu trích có đúng nguyên tác và đúng vị trí không? (b) có ý của học giả nào lọt vào giọng người kể không?
  (c) quan điểm bị phản bác đã được trình bày ở dạng mạnh nhất chưa? (d) có câu nào khiến người nghe nghĩ người kể đang khuyên tin hay làm điều gì không?
  (e) có trích dẫn giả nào không?
- Thư mục tập: `episodes/PNNN/`. File MP3: `SMA_PNNN_<Slug>_speech-only.mp3`. Không nhạc nền (quyết định 2026-10-16).
- Tên riêng (Socrates, Kālāma, Tử Lộ…) phải có mục trong `production/PRONUNCIATION_LEXICON.json` (`tools/names_add.py`; lexicon mang theo cả tên của series lịch sử, không ảnh hưởng gì). Thuật ngữ Hán Việt đọc bằng tiếng Việt;
  thuật ngữ Hy Lạp, Phạn, Pali đọc theo mặc định của engine rồi người dùng nghe duyệt.
- Render: Colab GPU. Trên điện thoại dùng `tools/colab_render.py` (colabjob); trên máy không có `colabjob` (phiên cloud) dùng đường Google Drive:
  `--bundle` → `MyDrive/Science_Media_Academy/colab_jobs/<job>/` → notebook `tools/colab/SMA_Drive_Render.ipynb` → `--ingest`.
- Nguồn không tải được trong phiên cloud (mạng chặn): người dùng có thể bỏ file văn bản hoặc PDF vào `MyDrive/Science_Media_Academy/philosophy_sources/`;
  agent đọc qua Google Drive connector, lưu bằng `tools/research.py add <tên> <file> <url gốc>` rồi trích như mọi nguồn cache khác.
- Trạng thái mỗi tập: `PLAN` → `PILOT` → `NEEDS_REVIEW` → (người dùng duyệt) → sản xuất đầy đủ. **Không xuất bản.**
