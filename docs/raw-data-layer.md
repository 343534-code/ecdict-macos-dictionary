# Phase 1：原始数据快照

`semantic_cleanup/raw_snapshot.py` 建立独立的 raw_entries 数据层，供后续语义重构读取。目前支持 ECDICT CSV、JSONL 和本项目使用的 MDX 1.0.28 样式标记。原词库和现有 Apple Dictionary 导出流程不被改写。

## 数据约定

每条记录包含 `word`、`phonetic`、`pos`、`translation_raw`、`definition`、`exchange`、`tags`、`bnc`、`coca`、`frq`、`collins`、`oxford`、`ecdict_version`。

- CSV/JSONL 的原字段、未知字段和原值类型全部保留在 `raw_fields`。只映射 `translation → translation_raw`、`tag → tags`；不清洗音标、不合并义项、不修改标点。
- 缺失字段用 `null`，并列入 `missing_fields`；原来的空字符串、数字零与缺失值保留区别。
- `frq` 与 `coca` 分别保存。未验证来源含义时，不把 `frq` 复制为 `coca`。
- MDX 使用已知样式标记抽取音标、释义、词性、时态文本和元数据；未识别元数据保留在 `mdx_metadata_raw`。原始键和正文同时以 Base64 保存，可逐字节还原，包括无效 UTF-8 和重定向指令。
- MDX 的 `translation_raw` 是从正文段抽取的文本视图，行分隔经过 HTML 换行拆分；需要原始空白和标签时使用 `mdx_body_base64`，不可把抽取视图当作原始字节。
- MDX 原始时态列表未必包含过去分词等明确标签，因此 `exchange` 保留时态原文，不推断标签。词性顺序及重复项也保留。
- `entry_id` 使用“源文件 SHA-256 + 源记录序号”。同词头多条记录不会互相覆盖，大小写和词头空白也不强制归一化。

## 快照文件

每次导入创建新目录，包含 `raw_entries.jsonl` 和 `manifest.json`。清单记录源哈希、源大小、版本、记录数量、导入器哈希和数据文件哈希。限制条数的导入显式标记为 `sample`。

不可变约束由接口执行：已有输出目录一律拒绝覆盖，不提供更新或追加接口；校验命令可检测内容变化。它不是操作系统级防篡改存储，拥有文件权限的人仍可以修改文件。生产流程应只读取通过校验的快照。

导入失败时可能留下部分数据，但不会写入完成清单，校验命令不接受这种目录。重新尝试时使用新目录；保留失败目录有利于诊断。导入前后均核对源哈希。全量导入逐条处理，不把全部词条加载进内存；MDX 读取库自身的索引开销另计。

## 使用

在仓库根目录执行（MDX 需要原项目的 readmdict/python-lzo 环境）：

```sh
python3 -m semantic_cleanup.raw_snapshot create SOURCE.mdx semantic_cleanup/work/raw-example \
  --format mdx --ecdict-version 1.0.28 --limit 26
python3 -m semantic_cleanup.raw_snapshot verify semantic_cleanup/work/raw-example
```

CSV/JSONL 改用对应的 `--format`。省略 `--limit` 才是全量导入。每次采用新的目录名；不要覆盖历史快照。

Phase 1 不把原始记录直接交给现有 `prepare_requests.py`：后者使用的 `frequency`、`exam_tags` 与新原始层字段不同。后续阶段需要显式适配，并携带 `entry_id`、源哈希和审核信息；不能通过缺省字段值悄悄筛掉原始词条。

## 2026-09-12 验证

- 37 项本地测试通过，包含现有导出/语义层测试及 7 项原始数据测试。
- 已使用真实 MDX 的前 26 条记录执行小样本导入与校验。该样本是按源顺序读取的数字词头，不是 Phase 0 的 26 个语义回归词，也不是 5,000 词 AI 候选集。
- 样本词头从 `00852` 至 `0335`，26 条释义非空，26 个记录 ID 各不相同。
- 源文件 SHA-256：`275e71b58fd359bfe649af1cbee533ea81770bdbc53ec4a34567f84720a5751b`，与 Phase 0 一致。
- 样本数据 SHA-256：`b46ea8c23c52ea933803e5613dbb3b499de15e006969c2d3d32dbaf47102ffa7`。
- 本地样本位于 `semantic_cleanup/work/raw-1.0.28-phase1-sample-20260912/`，由已有 Git 忽略规则排除。

本阶段完成了原始层接口和小样本验证。未执行全词库快照或 AI 请求，未构建、安装或发布词典；当前已安装版本的界面不受本阶段代码影响。语义 schema 的修订与候选处理属于后续阶段。
