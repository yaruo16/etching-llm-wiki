import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SLIDES = ROOT / "slides" / "index.html"

WIKI_FILES = {p.name[:2]: p for p in WIKI.glob("0*.md")}
NUM = re.compile(r"\d+(?:[.,]\d+)?")

GLOSSARY = [
    "微影", "遮罩", "光阻", "等向性", "非等向性", "底切", "深寬比", "選擇比",
    "電漿", "自由基", "離子", "RIE", "協同效應", "鈍化", "偏壓", "副產物",
    "活化能", "終點偵測", "過蝕刻", "均勻度", "動量轉移", "MEMS", "TSV", "晶格面",
]

APPROVED = ROOT / "tools" / "approved_labels.txt"

MAX_POINTS = 5
MAX_CHARS = 40


def visible(el):
    return re.sub(r"\s+", "", el.get_text())


def wiki_text(ids):
    return "".join(WIKI_FILES[i].read_text(encoding="utf-8") for i in ids if i in WIKI_FILES)


def explained(term, text):
    pats = [
        re.escape(term) + r".{0,3}[：＝（]",
        r"(叫|稱為|就是)" + re.escape(term),
        r"（[^）]*" + re.escape(term) + r"[^）]*）",
    ]
    return any(re.search(p, text) for p in pats)


def main():
    approved = set(APPROVED.read_text(encoding="utf-8").split()) if APPROVED.exists() else set()
    soup = BeautifulSoup(SLIDES.read_text(encoding="utf-8"), "html.parser")
    slides = soup.select("section.slide")
    source_err, beginner_err = [], []
    seen = set()

    for n, s in enumerate(slides, 1):
        meta = s.get("data-kind") == "meta"
        points = s.select("ul.pts li") + [tr for tr in s.select("table tr") if not tr.find("th")]

        if not meta:
            for p in points:
                wid = p.get("data-wiki")
                txt = visible(p)
                if not wid:
                    source_err.append(f"第{n}頁：沒有標 Wiki 頁 → {txt[:30]}")
                    continue
                if wid not in WIKI_FILES:
                    source_err.append(f"第{n}頁：Wiki {wid} 不存在")
                    continue
                ref = re.sub(r"\s+", "", wiki_text([wid]))
                for m in p.find_all("mark"):
                    for part in re.split(r"[（）()]", visible(m)):
                        if part and part not in ref:
                            source_err.append(f"第{n}頁：重點詞「{part}」在 Wiki {wid} 找不到")
                for num in NUM.findall(txt):
                    if num not in ref:
                        source_err.append(f"第{n}頁：數字 {num} 在 Wiki {wid} 找不到 → {txt[:30]}")
            ids = {p.get("data-wiki") for p in points if p.get("data-wiki")}
            ref_all = re.sub(r"\s+", "", wiki_text(ids))
            for t in s.select("svg text"):
                label = visible(t)
                core = re.sub(r"[＝=、／/+⁻]", "", label)
                if label in approved:
                    continue
                if core and not any(seg in ref_all for seg in re.split(r"[　＝]", label) if seg):
                    source_err.append(f"第{n}頁：圖上文字「{label}」在對應 Wiki 找不到原句（需人工確認）")

            if len(s.select("ul.pts li")) > MAX_POINTS:
                beginner_err.append(f"第{n}頁：重點超過 {MAX_POINTS} 點")
            for p in s.select("ul.pts li"):
                if len(visible(p)) > MAX_CHARS:
                    beginner_err.append(f"第{n}頁：句子太長（{len(visible(p))} 字）→ {visible(p)[:20]}…")

        page_text = visible(s)
        for term in GLOSSARY:
            if term in seen or term not in page_text:
                continue
            if term == "等向性" and "非等向性" in page_text and page_text.replace("非等向性", "").find("等向性") < 0:
                continue
            seen.add(term)
            holder = next((visible(e) for e in s.select("li, tr, .card, .sub, h2") if term in visible(e)), page_text)
            if not explained(term, holder):
                beginner_err.append(f"第{n}頁：名詞「{term}」第一次出現，沒有解釋")

    print("== 檢查 C2：簡報是否只用 Wiki 的內容 ==")
    for e in source_err:
        print("FAIL", e)
    print(f"{len(source_err)} 個問題")
    print("== 檢查 C3：對初學者會不會太難 ==")
    for e in beginner_err:
        print("FAIL", e)
    print(f"{len(beginner_err)} 個問題")
    sys.exit(1 if source_err or beginner_err else 0)


if __name__ == "__main__":
    main()
