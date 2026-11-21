import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SOURCES = ROOT / "sources"

TAG = re.compile(r"〔(S\d)〕")
NUM = re.compile(r"\d+(?:[.,]\d+)?")

GLOSSARY = [
    "微影", "遮罩", "光阻", "等向性", "非等向性", "底切", "深寬比", "選擇比",
    "電漿", "自由基", "離子", "RIE", "協同效應", "鈍化", "偏壓", "副產物",
    "活化能", "終點偵測", "過蝕刻", "均勻度", "動量轉移", "MEMS", "TSV", "晶格面",
]


def defined(term, text):
    pats = [
        re.escape(term) + r"[^，。\n]{0,8}[：＝]",
        re.escape(term) + r"（[^）]*）[^，。\n]{0,3}[：＝]",
        r"(叫|叫做|稱為|就是)\**" + re.escape(term),
        re.escape(term) + r"(就是|是指)",
        re.escape(term) + r"（[^）]*[\u4e00-\u9fff]{2,}[^）]*）",
        r"\|\s*\**" + re.escape(term) + r"[^|]*\|[^|]+\|",
        r"（[^）]*" + re.escape(term) + r"[^）]*）",
        r"\*\*" + re.escape(term) + r"[^*]*\*\*[：（]",
        r"#+\s*[^\n]*" + re.escape(term),
    ]
    return any(re.search(p, text) for p in pats)


def load_sources():
    out = {}
    for p in SOURCES.glob("S*.md"):
        out[p.name.split("-")[0]] = p.read_text(encoding="utf-8")
    return out


def content_lines(text):
    body = text.split("---", 2)[-1]
    lines = [l.strip() for l in body.splitlines()]
    nonempty = [l for l in lines if l]
    i = 0
    while i < len(nonempty):
        line = nonempty[i]
        if line.startswith("|"):
            j = i
            while j < len(nonempty) and nonempty[j].startswith("|"):
                j += 1
            prev = nonempty[i - 1] if i > 0 else ""
            nxt = nonempty[j] if j < len(nonempty) else ""
            yield "TABLE", nonempty[i:j], prev + nxt
            i = j
            continue
        i += 1
        if line.startswith("#") or line.startswith(">"):
            continue
        if "詳見" in line or line.startswith("建議閱讀") or line.startswith("讀取日期"):
            continue
        yield "LINE", line, None


def check_page(path, sources):
    errors = []
    text = path.read_text(encoding="utf-8")
    header = re.search(r"本頁來源：(.+)", text)
    if not header:
        return [f"{path.name}: 缺少「本頁來源」"]
    declared = set(re.findall(r"S\d", header.group(1)))
    used = set(TAG.findall(text))
    for s in declared | used:
        if s not in sources:
            errors.append(f"{path.name}: 來源 {s} 不存在")
    if used - declared:
        errors.append(f"{path.name}: 內文用了 {sorted(used - declared)} 但沒列在本頁來源")
    if declared - used:
        errors.append(f"{path.name}: 本頁來源列了 {sorted(declared - used)} 但內文沒用到")

    for kind, item, follow in content_lines(text):
        if kind == "TABLE":
            rows = [r for r in item if not re.match(r"^\|[\s\-|]+\|$", r)]
            block = "\n".join(rows)
            tags = set(TAG.findall(block)) | set(TAG.findall(follow or ""))
            if not tags:
                errors.append(f"{path.name}: 表格沒有來源標註 → {rows[0][:40]}")
                continue
            for row in rows[1:]:
                row_tags = set(TAG.findall(row)) or tags
                ref = "".join(sources.get(t, "") for t in row_tags)
                for n in NUM.findall(TAG.sub("", row)):
                    if n not in ref:
                        errors.append(f"{path.name}: 數字 {n} 在 {sorted(row_tags)} 筆記中找不到 → {row[:50]}")
            continue
        line = item
        tags = set(TAG.findall(line))
        if not tags:
            errors.append(f"{path.name}: 沒有來源標註 → {line[:50]}")
            continue
        ref = "".join(sources.get(t, "") for t in tags)
        for n in NUM.findall(TAG.sub("", re.sub(r"\[.*?\]\(.*?\)", "", line))):
            if n not in ref:
                errors.append(f"{path.name}: 數字 {n} 在 {sorted(tags)} 筆記中找不到 → {line[:50]}")
    return errors


def main():
    sources = load_sources()
    pages = sorted(p for p in WIKI.glob("0*.md"))
    all_errors = []
    for p in pages:
        all_errors += check_page(p, sources)
    index = (WIKI / "index.md").read_text(encoding="utf-8")
    for p in pages:
        if p.name not in index:
            all_errors.append(f"index.md: 目錄沒有 {p.name}")
    texts = "\n".join(p.read_text(encoding="utf-8") for p in pages)
    for term in GLOSSARY:
        if term in texts and not defined(term, texts):
            all_errors.append(f"名詞「{term}」在 Wiki 裡有用到，但沒有任何一頁給定義")
    for e in all_errors:
        print("FAIL", e)
    print(f"共 {len(pages)} 頁，{len(all_errors)} 個問題")
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
