# 半導體蝕刻 LLM Wiki

成大「生成式 AI」作業｜系統系碩二 李亞若（P16144108）

用 LLM Wiki 的方式整理「半導體蝕刻」入門知識，再只用 Wiki 當知識來源，做出一份教學用的 HTML 簡報。

- 網站：https://yaruo16.github.io/etching-llm-wiki/
- Wiki：https://yaruo16.github.io/etching-llm-wiki/wiki/
- 簡報：https://yaruo16.github.io/etching-llm-wiki/slides/

## 資料夾結構

```
etching-llm-wiki/
├── index.md                 網站首頁
├── _config.yml              GitHub Pages 設定
├── sources/                 5 篇來源的中文筆記（Wiki 只能根據這裡寫）
│   ├── S1-samsung.md
│   ├── S2-mks-etch-overview.md
│   ├── S3-mks-rie.md
│   ├── S4-epfl-definitions.md
│   └── S5-ieee-technav.md
├── wiki/                    LLM Wiki（每句標〔S#〕）
│   ├── index.md             Wiki 首頁目錄
│   ├── 01-what-is-etching.md
│   ├── 02-wet-etching.md
│   ├── 03-dry-etching.md
│   ├── 04-isotropic-anisotropic.md
│   ├── 05-rie.md
│   └── 06-key-concepts.md
├── slides/
│   └── index.html           教學簡報（單一 HTML）
├── process/
│   ├── workflow.md          loop / graph 設計（Mermaid）
│   ├── run-log.md           實際執行紀錄（逐節點）
│   └── reflection.md        反思
└── tools/
    ├── check_wiki.py        C1：Wiki 檢查
    ├── check_slides.py      C2＋C3：簡報檢查
    └── approved_labels.txt  人工確認過的圖上文字
```

## 5 篇資料來源

| 代號 | 資料 | 網址 |
|---|---|---|
| S1 | Samsung Newsroom〈Eight Major Steps to Semiconductor Fabrication, Part 5: Etching〉 | https://news.samsung.com/global/eight-major-steps-to-semiconductor-fabrication-part-5-etching-a-circuit-pattern |
| S2 | MKS Instruments〈Semiconductor Etching〉 | https://www.mks.com/n/etch-overview |
| S3 | MKS Instruments〈Reactive Ion Etching〉 | https://www.mks.com/n/reactive-ion-etching |
| S4 | EPFL CMi〈Etch definitions〉 | https://www.epfl.ch/research/facilities/cmi/process/etching/etch-definitions |
| S5 | IEEE TechNav〈Etching〉 | https://technav.ieee.org/topic/etching/ |

## 規則

1. Wiki 每一句都要標〔S1〕～〔S5〕，每頁開頭寫「本頁來源」。
2. 簡報只能用 Wiki 的內容。每個重點用 `data-wiki="01"` 這種屬性標對應的 Wiki 頁，畫面上會變成可以點的「Wiki 01」小標籤。
3. 簡報結構：是什麼 → 為什麼 → 怎麼運作 → 例子 → 重點整理 → 參考資料。

## 檢查程式

需要 Python 3 和 BeautifulSoup（`pip install beautifulsoup4`）。

```bash
python3 tools/check_wiki.py
python3 tools/check_slides.py
```

`check_wiki.py`（C1）檢查：
- 每頁有沒有「本頁來源」，標的來源和內文用到的有沒有對上
- 每一行、每個表格有沒有〔S#〕標註
- 句子裡的數字有沒有出現在那篇來源的筆記裡
- 專有名詞（`GLOSSARY` 清單）至少在一頁有定義

`check_slides.py` 檢查：
- C2：每個重點有沒有標 Wiki 頁；螢光筆標的詞、數字有沒有出現在那頁 Wiki；圖上文字如果找不到原句，要人工確認後加進 `approved_labels.txt`
- C3：每頁最多 5 點、每點最多 40 字；專有名詞第一次出現時有沒有解釋（冒號、等號、括號或「叫做…」）

有問題時程式會印出 `FAIL` 並回傳 1，全部通過才回傳 0。

## 簡報操作

- ← → 方向鍵、空白鍵、PageUp／PageDown 換頁；Home／End 跳到第一頁／最後一頁
- 手機可以左右滑
- 網址後面加 `#5` 可以直接開第 5 頁
- 字體用 Google Fonts 的「霞鶩文楷 TC」和 Caveat，做成手寫筆記風
