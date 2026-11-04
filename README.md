# Philosophy-Zk2 — "Hành Trình Tư Tưởng" (tên tạm)

Series audio triết học bằng tiếng Việt cho người bắt đầu từ con số 0: *Ta biết được gì? Cái gì là thật? Nên sống thế nào?
Sống cùng nhau ra sao? Đời có ý nghĩa gì?* Mỗi tập đọc nguyên tác qua bản dịch có tên, nêu các cách hiểu của học giả,
tái dựng lập luận và đưa ra phản biện mạnh nhất. Mục tiêu là dạy *cách nghĩ*, không dạy *tin gì*.

**Trạng thái (2026-11-04):** PLAN. Đã có series bible, chương trình học (miền `PHIL`, L0–L5) và kế hoạch tập P001 "Biết rằng mình không biết".
Chưa có nguồn đã cache, chưa có claim, kịch bản hay audio.

**Nguồn gốc:** tách từ [Science Media Academy](https://github.com/hadezkz002/science-media-academy) (commit `c79937b`), nơi có series lịch sử
"Hành Trình Nhân Loại". Repo này mang theo bản sao hạ tầng (cổng claim, pipeline TTS tiếng Việt, render Colab) và chạy được một mình.

## Đọc gì trước
1. [Series bible](curriculum/PHILOSOPHY_SERIES_BIBLE.md): nguyên tắc, nhãn claim, thang nguồn, bản đồ 7 mùa P001–P035.
2. [AGENTS.md](AGENTS.md): hướng dẫn bàn giao cho agent, lệnh chuẩn, ràng buộc.
3. [Tập P001](episodes/P001/brief.md) và [kế hoạch nghiên cứu](episodes/P001/research_plan.md).
4. [Playbook sản xuất](production/EPISODE_PLAYBOOK.md), [chuẩn biên tập](standards/EDITORIAL_GUIDE.md), [chính sách kiểm chứng](standards/FACT_CHECK_POLICY.md).

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `curriculum/` | Series bible; `curriculum.json` (6 chủ đề PHIL, L0–L5) |
| `episodes/PNNN/` | Mỗi tập: `brief.md`, `outline.md`, `research_plan.md`, `metadata.json`; sau này `script.md`, `claims.csv`, `sources.md`, review, QA |
| `research/PHILOSOPHY_SOURCE_REGISTER.md` | Sổ nguồn chung (mã `PS`) |
| `standards/` | Chuẩn biên tập, chính sách kiểm chứng, schema metadata tập |
| `src/sma/` | Cổng claim (`claims.py`), lập kế hoạch/render/master audio (`produce.py`), chuẩn hóa văn bản, tên riêng, runner TTS |
| `tools/` | `research.py` (cache nguồn), `sources_build.py`, `names_add.py`, `colab_render.py` + `colab/SMA_Drive_Render.ipynb`, `run_episode.sh`, `asr_report.py`, `bench_tts.py` |
| `production/` | Playbook, prompt review, engine TTS, lexicon phát âm |

## Lệnh chuẩn

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

```bash
PYTHONPATH=src python3 -m sma.claims episodes/P001 --release
```

```bash
python3 tools/research.py web sep_socrates https://plato.stanford.edu/entries/socrates/
```

```bash
PYTHONPATH=src python3 -m sma.produce plan episodes/P001 --engine vieneu-turbo-fp32
```

```bash
python3 tools/colab_render.py episodes/P001
```

## Cài đặt audio (tóm tắt)
- Engine chính `vieneu-turbo-fp32` (VieNeu-TTS v3 Turbo, Apache-2.0, giọng preset "Hải Đăng", watermark bật). Cấu hình: `production/engines.json`;
  venv cục bộ `.venv-vieneu/` (không commit). Đánh giá engine: `reports/TTS_BENCHMARK.md`; kiến trúc: `production/AUDIO_PIPELINE.md`.
- Render nặng chạy trên Colab GPU: qua `colabjob` trên điện thoại, hoặc qua Google Drive bằng notebook `tools/colab/SMA_Drive_Render.ipynb`
  (`tools/colab_render.py --bundle` / `--ingest`). Planning, gate, master và QA chạy cục bộ.
- Không commit audio, model hay venv (`.gitignore`).

## Giới hạn trung thực
- Reviewer là AI agent tách biệt; chưa có chuyên gia triết học người thật duyệt.
- Không ai trong quy trình nghe audio bằng tai; người dùng phải nghe duyệt trước khi phát hành.
- Các chi tiết nguyên tác trong brief/outline/kế hoạch P001 là **ý định cần kiểm tra**, viết khi chưa đọc được nguồn.
