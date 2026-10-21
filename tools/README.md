# tools/ 使用说明（thinking_code）

双语书《thinking_code》本地维护脚本。**不参与 jupyter-book 构建**，只在润色、校对、同步时使用。
本目录不进 git（`.gitignore` 已忽略），改坏了可以直接重写。

## 目录

| 路径 | 内容 |
|---|---|
| `thinking_code/` | 日文原稿（只作对照，不改） |
| `thinking_code_cn/` | 中文版（28 章，独立的一本 jupyter-book） |
| `tools/check_sync.py` | 日文 ⇄ 中文的结构一致性检查 |
| `tools/exec_notebook.py` | 用 pixi 的 python 执行 notebook 并写回输出 |
| `tools/nbedit.py` | 按本书约定（indent=1 / CRLF / 末尾无换行）读写 notebook |
| `tools/glossary.tsv` | 术语表（日语 → 中文），`zh_term_check.py` 直接读它 |
| `tools/zh_style_lint.py` | 文风门禁：句长、短句/长句比例、问号、你/您、全角括号、口语词 |
| `tools/zh_flow_lint.py` | 可疑句排序（不判好坏，按可疑度打分） |
| `tools/zh_sentence_dump.py` | 打印门禁实际统计的每一句及汉字数 |
| `tools/zh_tune_hint.py` | 紧凑版：只列短句、最长句 |
| `tools/zh_term_check.py` | 术语一致性 + 列表被压平检测 |
| `tools/zh_auto_merge.py` | 机械合并相邻短句（⚠️ 少用，见下文） |
| `index_redirect.html` / `404.html` | 站点首页与旧 URL 跳转 |

## 日常用法

```powershell
$env:MKL_THREADING_LAYER='TBB'
$py = "C:\pixi_env\.pixi\envs\default\python.exe"
Set-Location C:\Users\ruoyu\Documents\notebooks\thinking_code

# 结构检查：全章 / 单章
& $py tools\check_sync.py
& $py tools\check_sync.py z3_intro

# 新增章节后重写中文版 _toc.yml（按日文目录顺序，只列已存在的章节）
& $py tools\check_sync.py --update-toc

# 文风门禁（--diff 打印越界句；--soft 把硬指标降为 WARN）
& $py tools\zh_style_lint.py --all
& $py tools\zh_style_lint.py z3_intro --diff

# 逐句核对
& $py tools\zh_sentence_dump.py z3_intro
& $py tools\zh_tune_hint.py z3_intro
& $py tools\zh_flow_lint.py z3_intro -v

# 术语与排版
& $py tools\zh_term_check.py
```

## 检查内容

`check_sync.py`：

- cell 数、cell 类型序列、cell id 序列
- markdown 标题序列（防止整 cell 替换时丢标题）
- MyST 标签 `(label)=` 的集合（跨章链接依赖它）
- 中文版 markdown 里的假名、未执行代码格、error 输出
- markdown 代码围栏个数

`zh_term_check.py` 的术语对全部来自 `glossary.tsv`，因此改术语表即可扩展检查。

## 口径与注意事项

- **门禁只作参考。** 这本书的章节多是「规则 + 步骤 + 代码」，长句比例天然偏低；
  低于 0.10 时先判断是不是体裁造成的，不要为了进带去合并句子。
- `zh_style_lint.py` 会跳过以行内代码或 `$` 开头的段落，讲机制的那一段若以 `BitVec`、`Solver`
  之类开头就整段不计入统计。遇到这种章节，用 `zh_sentence_dump.py` 看实际句子。
- 清单／参考型章节（`ortools-sat_api`、`z3_data_types`、`z3_gray_code`、`ortools-sat_number_link`）
  已列入 `SOFT_CHAPTERS`，硬指标降级为 WARN。
- **写回约定**：JSON `indent=1`、`ensure_ascii=False`、CRLF、**末尾没有换行符**。
  `nbedit.py` 与 `zh_term_check.py --fix` 都按这个约定写；`nbformat` 直写会加换行并重排键序，
  因此改完务必跑一次逐字节往返检查。
- `zh_auto_merge.py` 是机械改写，只在明确要调节奏时用；它不看语义，容易把转折句合成一句。

## 说明

- 日文原稿只作对照，不修改；中文版是唯一在维护的正文。
- `thinking_code_cn/helper/`、`data/`、`images/` 是独立副本。
- 构建部署见 `.github/workflows/deploy.yml`：日语 → `site/ja/`，中文 → `site/zh/`。
