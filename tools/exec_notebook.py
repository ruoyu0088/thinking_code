#!/usr/bin/env python3
"""在本地执行 notebook 并把输出写回（用 jupyter 内核）。

用法:
    python tools/exec_notebook.py thinking_code_cn/z3_intro.ipynb [more.ipynb ...]

注意: 用 C:\\pixi_env 的 python 运行，才能用到 z3 / pysat / ortools。
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def run(path: Path) -> bool:
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
        allow_errors=False,
    )
    client.execute()
    nbformat.write(nb, path)

    errors = 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                errors += 1
                print(f"  [{path.name}] cell {i}: {out.get('ename')}: {out.get('evalue')}")
    print(f"{'OK  ' if errors == 0 else 'FAIL'} {path} ({len(nb.cells)} cells)")
    return errors == 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    ok = True
    for arg in sys.argv[1:]:
        ok = run(Path(arg).resolve()) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
