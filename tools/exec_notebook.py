#!/usr/bin/env python3
"""thinking_code_cn 用：在本地执行 notebook 并把输出写回。

用法（书根目录下）:

    python tools/exec_notebook.py thinking_code_cn/z3_intro.ipynb [more ...]

必须用 C:\\pixi_env 的 python（z3-solver / python-sat / ortools / numpy / scipy /
sympy / matplotlib 都在里面），并设 MKL_THREADING_LAYER=TBB。

写回规则（为了避免无意义 diff）:
- 删掉 nbclient 塞进 cell metadata 的 execution 时间戳
- 保持文件原来的行尾（本书是 CRLF）
- **末尾不加换行**（本书所有 notebook 都不以换行结尾）

⚠️ 只对确实需要刷新输出的章节运行；本项目的正文润色不改 code cell，
因此日常校对不需要执行它。
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

_ENV_BIN = Path(sys.executable).resolve().parent / "Library" / "bin"
if _ENV_BIN.exists():
    import os
    os.environ["PATH"] = str(_ENV_BIN) + os.pathsep + os.environ.get("PATH", "")


def _write_like(original_bytes: bytes, nb, path: Path) -> None:
    text = nbformat.writes(nb, version=4)
    if text.endswith("\n"):
        text = text[:-1]
    if b"\r\n" in original_bytes:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def run(path: Path) -> bool:
    original = path.read_bytes()
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=1800,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
        allow_errors=True,
    )
    client.execute()

    for cell in nb.cells:
        cell.get("metadata", {}).pop("execution", None)
    _write_like(original, nb, path)

    failed = 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                failed += 1
                head = "".join(cell.source).splitlines()
                head = head[0][:60] if head else ""
                print(f"  [{path.name}] cell {i}: {out.get('ename')}: {out.get('evalue')}  <- {head}")
    print(f"{path.name}: {'OK' if not failed else f'{failed} ERROR cell(s)'}")
    return failed == 0


if __name__ == "__main__":
    ok = True
    for arg in sys.argv[1:]:
        ok &= run(Path(arg))
    sys.exit(0 if ok else 1)
