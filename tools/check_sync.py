#!/usr/bin/env python3
"""日文原稿 ⇄ 中文版结构检查（thinking_code / thinking_code_cn）。

看的是「结构有没有走样」，不是译文质量：

- 两边 cell 数、cell 类型序列、cell id 序列是否一致
- markdown 标题序列是否一致（防止整 cell 替换时丢标题）
- MyST 标签 `(label)=` 的集合是否一致（跨章链接依赖它）
- 中文版 markdown 里有没有残留假名
- 中文版有没有未执行的代码格、error 输出
- markdown 代码围栏的个数是否一致

用法（书根目录下）::

    python tools/check_sync.py                 # 全部章节
    python tools/check_sync.py z3_intro ...    # 指定章节
    python tools/check_sync.py --update-toc    # 按日文目录顺序重写中文版 _toc.yml

只读，不修改 notebook。中文版文件末尾没有换行符，本脚本不写 notebook。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "thinking_code"
CN = ROOT / "thinking_code_cn"
KANA = re.compile(r"[\u3040-\u30ff]")
LABEL = re.compile(r"^\(([A-Za-z0-9\-_]+)\)=\s*$", re.M)


def load(path: Path) -> dict:
    return json.loads(path.read_bytes())


def src(cell) -> str:
    s = cell["source"]
    return "".join(s) if isinstance(s, list) else s


def heads(nb: dict) -> list[str]:
    """markdown 的标题行；先去掉围栏，免得把代码注释当成标题。"""
    out = []
    for c in nb["cells"]:
        if c["cell_type"] != "markdown":
            continue
        body = re.sub(r"```.*?```", "", src(c), flags=re.S)
        out.extend(ln.rstrip() for ln in body.split("\n") if ln.startswith("#"))
    return out


def levels(nb: dict) -> list[int]:
    """标题的层级序列。标题文字本身是译文，只能比层级与个数。"""
    return [len(h) - len(h.lstrip("#")) for h in heads(nb)]


def labels(nb: dict) -> set[str]:
    out = []
    for c in nb["cells"]:
        if c["cell_type"] == "markdown":
            out.extend(LABEL.findall(src(c)))
    return set(out)


def fences(nb: dict) -> int:
    return sum(len(re.findall(r"```", src(c))) for c in nb["cells"] if c["cell_type"] == "markdown") // 2


def check(name: str) -> bool:
    ja_path, cn_path = JA / f"{name}.ipynb", CN / f"{name}.ipynb"
    if not cn_path.exists():
        print(f"{name:44} SKIP (中文版未翻译)")
        return True
    if not ja_path.exists():
        print(f"{name:44} MISSING (ja)")
        return False
    ja, cn = load(ja_path), load(cn_path)
    problems: list[str] = []

    if len(ja["cells"]) != len(cn["cells"]):
        problems.append(f"cells {len(ja['cells'])}!={len(cn['cells'])}")
    if [c["cell_type"] for c in ja["cells"]] != [c["cell_type"] for c in cn["cells"]]:
        problems.append("cell-type sequence differs")
    if [c.get("id") for c in ja["cells"]] != [c.get("id") for c in cn["cells"]]:
        problems.append("cell-id sequence differs")
    if levels(ja) != levels(cn):
        problems.append(f"heading levels differ: ja={levels(ja)} cn={levels(cn)}")
    if labels(ja) != labels(cn):
        problems.append(f"myst labels differ: ja-cn={sorted(labels(ja) - labels(cn))} cn-ja={sorted(labels(cn) - labels(ja))}")
    if fences(ja) != fences(cn):
        problems.append(f"fences {fences(ja)}!={fences(cn)}")

    kana_md = sum(len(KANA.findall(src(c))) for c in cn["cells"] if c["cell_type"] == "markdown")
    if kana_md:
        problems.append(f"kana(md)={kana_md}")

    # 代码格里的假名多是数据值，只提示不算失败
    kana_code = [i for i, c in enumerate(cn["cells"])
                 if c["cell_type"] == "code" and KANA.search(src(c))]

    unexec = [i for i, c in enumerate(cn["cells"])
              if c["cell_type"] == "code" and src(c).strip() and c.get("execution_count") is None]
    if unexec:
        problems.append(f"unexecuted={unexec[:5]}")

    errors = [(i, o.get("ename")) for i, c in enumerate(cn["cells"]) if c["cell_type"] == "code"
              for o in c.get("outputs", []) if o.get("output_type") == "error"]
    if errors:
        problems.append(f"errors={errors[:5]}")

    status = "OK" if not problems else "!! " + "; ".join(problems)
    if kana_code:
        status += f"  (kana in code cells: {kana_code})"
    print(f"{name:44} {status}")
    return not problems


def update_toc() -> None:
    """按日文版 _toc.yml 的顺序，只列出中文版里已经存在的章节。"""
    order = [m.strip() for m in re.findall(r"-\s*file:\s*(\S+)", (JA / "_toc.yml").read_text(encoding="utf-8"))]
    have = [n for n in order if (CN / f"{n}.ipynb").exists()]
    parts = [("Z3", [n for n in have if n.startswith("z3_")]),
             ("PySat", [n for n in have if n.startswith("sat_")]),
             ("OrTools", [n for n in have if n.startswith("ortools")])]
    lines = ["# 由 tools/check_sync.py --update-toc 生成：只列出已翻译的章节",
             "format: jb-book", "root: index", "parts:"]
    for cap, names in parts:
        if not names:
            continue
        lines.append(f"- caption: {cap}")
        lines.append("  chapters:")
        lines.extend(f"  - file: {n}" for n in names)
    (CN / "_toc.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已写入 {CN / '_toc.yml'}（{len(have)} 章）")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--update-toc" in sys.argv:
        update_toc()
        sys.exit(0)
    names = args or [f[:-6] for f in sorted(p.name for p in JA.glob("*.ipynb"))]
    ok = all([check(n) for n in names])
    print(f"\n{len(names)} 章；{'全部一致' if ok else '有差异'}")
    sys.exit(0 if ok else 1)
