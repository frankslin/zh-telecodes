#!/usr/bin/env python3
"""Build data.js (window.TELECODE) from the files in sources/.

Run from the repo root:  python3 scripts/gen_data.py

Inputs
  sources/Unihan_Telegraph.txt            kMainlandTelegraph / kTaiwanTelegraph (Unicode Unihan)
  sources/njstar-*-codebook.html          NJStar code books — only used for non-Hanzi codes
                                          (month signs, bopomofo, letters, punctuation),
                                          which Unihan does not cover
  sources/swift_eccc_v2.xlsx              SWIFT e-CCC v2 (simplified + traditional per code)
  sources/hkhc-ccc-source-v2.txt          hkhc/ccc (github.com/hkhc/ccc @920846e, Apache-2.0),
                                          a community table that layers several readings per code
  sources/Unihan_STVariants.txt           kSimplifiedVariant / kTraditionalVariant
  sources/opencc/*.txt                    OpenCC single-character S/T and regional variants
                                          (plus SWIFT's own S/T pairs)

Output
  data.js  window.TELECODE = {
    meta,
    cn:  {code: char},            mainland 标准电码本 (1983) per Unihan
    tw:  {code: char},            Taiwan 中文電碼 per Unihan (a char may own 2 codes)
    sw:  {code: [simp, trad, note?]}   SWIFT e-CCC v2; "" = blank side
    hk:  {code: "陳c陈"}             hkhc/ccc, packed: each char is preceded by its layer
                                      mark (none = base; o=old, 1/2/3=s1–s3, c=china1, C=china2)
    nh:  {cn: [codes], tw: [codes]}    codes that are non-Hanzi (from NJStar)
    v:   {char: "related chars"}       S/T + regional variants, for cross-lookup
  }
"""
import html
import json
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
OUT = ROOT / "data.js"


def cp2ch(s):
    return chr(int(s.removeprefix("U+"), 16))


def read_unihan_telegraph():
    tables = {"kMainlandTelegraph": {}, "kTaiwanTelegraph": {}}
    version = ""
    for line in (SRC / "Unihan_Telegraph.txt").open(encoding="utf-8"):
        if line.startswith("# Unicode Version"):
            version = line.split("Version", 1)[1].strip()
        if line.startswith("#") or not line.strip():
            continue
        cp, key, val = line.rstrip("\n").split("\t")
        for code in val.split():
            assert code not in tables[key], (key, code)
            tables[key][code] = cp2ch(cp)
    return tables["kMainlandTelegraph"], tables["kTaiwanTelegraph"], version


def read_njstar_book(path):
    t = path.read_text(encoding="utf-8")
    out = {}
    for code_row, han_row in re.findall(r"<tr class=code>(.*?)</tr>\s*<tr class=hanzi>(.*?)</tr>", t, re.S):
        codes = re.findall(r"<td>(\d{4})</td>", code_row)
        cells = re.findall(r"<td>(.*?)</td>", han_row)
        for code, cell in zip(codes, cells):
            chars = re.findall(r"&#x([0-9A-Fa-f]+);", cell)
            if chars:
                out[code] = "".join(chr(int(x, 16)) for x in chars)
    return out


st_pairs = []  # SWIFT's curated simplified/traditional pairs, reused as variant links


def read_swift():
    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # embedded .wmf illustration
        wb = openpyxl.load_workbook(SRC / "swift_eccc_v2.xlsx", read_only=True)
    ws = wb.worksheets[2]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        code = str(r[0]).strip()
        simp = (r[1] or "").strip()
        trad = (r[3] or "").strip()
        status, remark = (r[5] or "").strip(), (r[6] or "").strip()
        if not simp and not trad:
            continue
        note = ""
        if "无法录入" in remark:
            # One side could not be typed in 2014; SWIFT left it blank.
            note = "繁體無法錄入" if not trad else "簡體無法錄入" if not simp else ""
        # Row 6812 has a trailing space ("醃 ") — stripped above. Row 8788 lists
        # U+7295 for the traditional side but the cell holds 犔 (U+7294); trust the cell.
        out[code] = [simp, trad] + ([note] if note else [])
        if status == "繁简正确对应":
            st_pairs.append((simp, trad))
    return out


HKHC_LAYERS = {"old": "o", "s1": "1", "s2": "2", "s3": "3", "china1": "c", "china2": "C"}


def read_hkhc():
    """Each line: code, then (optional "g_<layer> ")U+XXXX<TAB>char pairs.

    The file was scraped from an HTML table, so a few cells are irregular: an
    astral char shown as "&#x...;(<script>…)", a stray ";" or a space instead of
    a tab. The code point is authoritative; the glyph column is ignored.
    """
    out = {}
    pair = re.compile(r"(?:g_(\w+)\s+)?U\+([0-9A-Fa-f]{4,6})")
    for line in (SRC / "hkhc-ccc-source-v2.txt").open(encoding="utf-8"):
        m = re.match(r"^(\d{4})\t(.*)$", line.rstrip("\n"))
        if not m:
            continue
        code, rest = m.groups()
        rest = re.sub(r"\(<script.*$", "", rest)  # trailing markup after an entity
        entries = []
        for layer, cp in pair.findall(rest):
            assert not layer or layer in HKHC_LAYERS, (code, layer)
            ch = chr(int(cp, 16))
            if [layer, ch] not in entries:
                entries.append([layer, ch])
        if entries:
            out[code] = "".join(HKHC_LAYERS.get(layer, "") + ch for layer, ch in entries)
    return out


def read_variants():
    edges = defaultdict(set)

    def add(a, b):
        if a != b and len(a) == 1 and len(b) == 1:
            edges[a].add(b)
            edges[b].add(a)

    for line in (SRC / "Unihan_STVariants.txt").open(encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        cp, _key, val = line.rstrip("\n").split("\t")
        for v in val.split():
            add(cp2ch(cp), cp2ch(v.split("<")[0]))
    for name in ["STCharacters", "TSCharacters", "TWVariants", "HKVariants"]:
        for line in (SRC / "opencc" / f"{name}.txt").open(encoding="utf-8"):
            if line.startswith("#") or "\t" not in line:
                continue
            k, vals = line.rstrip("\n").split("\t")
            for v in vals.split():
                add(k, v)
    for a, b in st_pairs:  # e.g. 凼/氹, which neither Unihan nor OpenCC links
        add(a, b)
    return edges


def main():
    cn, tw, version = read_unihan_telegraph()
    nj_cn = read_njstar_book(SRC / "njstar-mainland-codebook.html")
    nj_tw = read_njstar_book(SRC / "njstar-taiwan-codebook.html")

    # Unihan and NJStar must agree on every Hanzi code; NJStar adds non-Hanzi only.
    nonhan = {}
    for name, uni, nj in [("cn", cn, nj_cn), ("tw", tw, nj_tw)]:
        extra = []
        for code, ch in nj.items():
            if code in uni:
                if uni[code] != ch:
                    sys.exit(f"{name} {code}: Unihan {uni[code]} != NJStar {ch}")
            else:
                uni[code] = ch
                extra.append(code)
        missing = [c for c in uni if c not in nj]
        if missing:
            print(f"note: {name} codes in Unihan but not in NJStar book: {missing[:10]}…")
        nonhan[name] = sorted(extra)

    sw = read_swift()
    hk = read_hkhc()

    edges = read_variants()
    chars = set(cn.values()) | set(tw.values())
    for s, t, *_ in sw.values():
        chars.update(c for c in (s, t) if c)
    for packed in hk.values():
        chars.update(ch for ch in packed if ord(ch) > 0x7F)
    chars = {c for c in chars if len(c) == 1}
    # Keep only variant links that lead somewhere useful: to a char of any table,
    # plus one extra hop (國→国→國 style chains are covered by symmetric edges).
    variants = {}
    pool = chars | {n for c in chars for n in edges.get(c, ())}
    for c in sorted(pool):
        near = set(edges.get(c, ()))
        for n in list(near):
            near |= edges.get(n, set())
        near.discard(c)
        near &= chars
        if near:
            variants[c] = "".join(sorted(near))

    def sort_codes(d):
        return dict(sorted(d.items()))

    data = {
        "meta": {
            "unicode": version,
            "counts": {
                "cn": len(cn), "cnHan": len(cn) - len(nonhan["cn"]),
                "tw": len(tw), "twHan": len(tw) - len(nonhan["tw"]),
                "sw": len(sw),
                "hk": len(hk), "hkChars": sum(sum(ord(c) > 0x7F for c in v) for v in hk.values()),
            },
        },
        "cn": sort_codes(cn),
        "tw": sort_codes(tw),
        "sw": sort_codes(sw),
        "hk": sort_codes(hk),
        "nh": nonhan,
        "v": variants,
    }
    with OUT.open("w", encoding="utf-8") as f:
        f.write("window.TELECODE=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("unicode", version, "| counts", data["meta"]["counts"], "| variants", len(variants),
          "| bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
