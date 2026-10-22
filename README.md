# 考えるコード ― 制約と最適化の冒険

https://ruoyu0088.github.io/thinking_code

## セットアップ / 使用说明

両言語で共通の資産は `shared/`（`helper/`, `data/`, `images/`, `_static/`）にあります。
各言語のディレクトリにある同名のディレクトリは、ビルド前にコピーされる生成物で、Git では管理していません。
两种语言共用的资源放在 `shared/`，各语言目录下的同名目录由脚本生成，不纳入 Git。

### ノートブックを実行する / 运行 notebook

```bash
python sync_assets.py --apply --all
cd thinking_code        # 日本語版 / 日文版
# cd thinking_code_cn   # 中国語版 / 中文版
jupyter lab
```

- Jupyter は必ず本のディレクトリで起動してください。notebook の `data/...` と `import helper` はカレントディレクトリ基準です。
- Jupyter 必须从书目录启动，notebook 里的 `data/...` 和 `import helper` 都按当前目录解析。
- 実行依存 / 运行依赖: `numpy`, `matplotlib`, `z3-solver`, `ortools`, `python-sat`, `sympy`, `scipy`（一部の章 / 个别章节: `polars`, `beautifulsoup4`）。
- `requirements.txt` はビルド用です / 只用于构建站点。

### ビルド / 构建

```bash
python sync_assets.py --apply --all
jupyter-book build thinking_code
jupyter-book build thinking_code_cn
```

### 資産の変更 / 修改资源

`shared/` だけを編集し、`python sync_assets.py --apply --all` を実行してください。
`python sync_assets.py --check` で同期ずれを確認できます。
只修改 `shared/`，然后运行同步脚本；`--check` 可以检查是否同步。
