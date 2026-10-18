# tools/ 使用说明

双语文档的辅助脚本。**这些脚本不参与书本身的构建**，只在本地维护时使用。

## 目录

| 路径 | 内容 |
|---|---|
| `thinking_code/` | 日语书（正本，目录名不改） |
| `thinking_code_cn/` | 中文书（独立的一本 jupyter-book） |
| `tools/check_sync.py` | 检查双语 notebook 是否一致 / 生成给 AI 的同步提示 |
| `tools/exec_notebook.py` | 用 pixi 的 python 执行 notebook 并写回输出 |
| `tools/glossary.tsv` | 术语表（日语 → 中文） |
| `index_redirect.html` | 站点首页，按浏览器语言跳到 `/ja/` 或 `/zh/` |
| `404.html` | 旧 URL（`/xxx.html`）自动转到 `/ja/xxx.html` |

## 日常用法

```bash
# 全部检查：哪边改过、结构是否一致、中文页有没有假名
C:/pixi_env/.pixi/envs/default/python.exe tools/check_sync.py

# 只看某一章
... tools/check_sync.py z3_intro

# 生成"让 AI 同步这一章"的提示（复制粘贴给 Hermes）
... tools/check_sync.py --prompt z3_intro

# 翻译/修改完成后，执行 notebook 刷新输出
... tools/exec_notebook.py thinking_code_cn/z3_intro.ipynb

# 同步完成后，记录新的基准（下次就能判断哪边更新）
... tools/check_sync.py --update-state z3_intro

# 新增章节后，重新生成中文版 _toc.yml（只列已翻译的章节）
... tools/check_sync.py --update-toc
```

## 检查内容

- cell 数、cell 类型顺序是否一致
- MyST 标签（`(z3-send-more-money)=` 等）是否两边都有 —— 跨章链接依赖它
- 中文页是否残留平假名/片假名
- 代码格 token 流是否一致（忽略注释和字符串字面量，所以翻译不会误报）
- 用 `.sync_state.json` 的哈希基线判断"日语改了"还是"中文改了"

## 说明

- 两边都可以改，`check_sync.py` 只判断哪边更新，然后给出同步方向；实际翻译由 AI 完成。
- `thinking_code_cn/helper/`、`data/`、`images/` 是独立副本，改了日语侧要记得同步。
- 构建部署见 `.github/workflows/deploy.yml`：日语 → `site/ja/`，中文 → `site/zh/`。
