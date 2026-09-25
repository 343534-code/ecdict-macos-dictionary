# Phase 2：语义候选数据契约

本阶段交付 `schema-v2.json`、结构校验/审核报告入口 `candidate_v2.py` 和三个设计样例。旧版 `schema.json`、SQLite 导入与 Apple Dictionary 生成器继续使用 1.0；新候选不能直接写入旧库。这里的 `2.0` 是数据格式版本，不表示已发布词典 v2.0.0。

## 结构与原始层关联

| 字段 | 用途与约束 |
| --- | --- |
| schema_version | 必须显式为 `2.0`，不自动升级旧数据 |
| word | 保留精确词头，来源关联时不忽略大小写或空白 |
| pronunciation | IPA 和 region 对象数组；region 为 UK、US 或 unspecified。没有地区依据时用 unspecified |
| senses | 多词性、多义项候选；每个义项有稳定标识 sense_id 和词性内连续编号 sense_number |
| english_definition | 一句简单英语，1–15 个英文词、最多 180 字符 |
| chinese_definition | 最多 72 字符；用 `；` 分隔，拒绝空段、重复段、顿号和半角分号 |
| confidence | 每个义项必填的 0–1 有限数值；代表生成者自评，不是正确率或审核结论 |
| source_entry_ids | 每个义项至少关联一个原始记录；必须属于词条 provenance 引用集合 |
| examples | 英中成对且声明生成来源；整词最多一例，允许零例 |
| usage_notes / domain | 每义项最多两条提示；领域用完整名称，无领域时为 null |
| learning_priority | most_common、exam_common、specialist 或 unknown；这是待核查分类，不是从词频自动推出的事实 |
| morphology | 明确标签和词形；过去式与过去分词可以分别保留，不能因为简化显示而丢掉原有语法信息 |
| exam_tags | 受控考试名列表，无数据时为空数组 |
| frequency | bnc、coca、frq、collins、oxford_3000 分别保留；未知为 null，不能把未知排名写为零 |
| provenance | 来源类型、源 SHA-256、原始记录 ID、ECDICT 版本、生成器及版本、提示词版本、生成时间 |

原始 ID 格式沿用 Phase 1 的 `source_sha256:ordinal`。同一个候选可以引用相同源快照中的多个同词头记录，因此不必因原数据把同一词性分成多条就生成多个候选词条。每个候选仍必须精确对应这些原记录的词头。

通过 `--raw-snapshot` 提供快照时，先校验 Phase 1 清单与数据哈希，再检查引用、词头和 ECDICT 版本。`raw_source_verified` 仅说明引用对应真实快照，不证明生成的释义受原文支持，也不证明模型生成的词频或音标正确。

## 结构校验与采用决策

所有对象拒绝未知字段，避免把模型自行输出的 `approved` 等字段当作授权。Python 使用同一 JSON Schema 校验结构，并额外检查跨字段规则：编号连续、总例句数、英文词数、精确重复及来源引用关系。校验失败抛出错误；不悄悄修补候选、不自动合并不同 sense。

JSON Schema 的 64 个义项是输入安全上限，不是展示目标：

- 1–3 个：符合首屏数量目标，仍需语义审核。
- 4–5 个：合法候选，标记超过默认展示目标。
- 超过 5 个：保留候选并标记专门审核，不截断丢义项。
- 超过 64 个：拒绝输入。

置信度低于 0.8 会增加审核原因。0.8 是当前工程分流阈值，尚未校准；高于阈值也不代表正确。当前所有候选都返回 `needs_review` 和 `production_eligible: false`，不允许生成者自评直接变成可发布状态。

必须由后续独立审核处理的内容包括：

- 义项是否应合并或拆分，是否遗漏或臆造语义；
- 例句是否体现它所在的义项，翻译是否贴切；
- 词频、考试、词形和音标是否忠实于来源；
- 英文是否自然、原创且面向学习者；
- 常用/考试/专业义的排序是否有依据；
- 实际 Dictionary.app 与 Look Up 首屏是否可读。

结构程序不能自动证明“没有幻觉”或“没有复制”。例如，把发布软件的例句放在“释放囚犯”义项下，仍可能通过结构校验，必须由语义审核发现。

## 可查看的设计样例

样例位置：`semantic_cleanup/examples-v2/`。这些是本次设计演示，不是从真实原始快照验证过的成品词条。其全零源哈希、演示版本号、生成时间及置信度仅用于表达数据结构；`source=design_example` 会明确阻止生产使用。

`release.json` 的组织如下：

```text
release /rɪˈliːs/
n.
① the act of allowing someone or something to go free
  释放；解放
② the act of making something available to the public
  发布；发行
vt.
① to allow someone or something to go free
  释放；放走
② to make something available to the public
  发布；发行；推出
  The team released a new app today.
  团队今天发布了一款新应用。
```

例句属于 vt.②“发布”而不是 vt.①“释放”。`bank.json` 分开“银行”和“河岸”；`break.json` 分开“打破”“休息”和“违反”。这些文件演示所需结构，不暗示程序已能判断这些语义边界。

## 本地验证

仅新校验工具需要 `requirements-semantic.txt` 中的 jsonschema。旧导出器无需新增依赖。

```sh
python3 -m semantic_cleanup.candidate_v2 semantic_cleanup/examples-v2/release.json
python3 -m semantic_cleanup.candidate_v2 path/to/candidate.json --raw-snapshot path/to/snapshot
python3 -m unittest discover -s tests -p 'test_*.py'
```

命令输出独立审核报告，不改写候选、写入数据库或调用模型。

2026-09-12 验证：51 项测试通过（37 项现有测试、14 项新测试）。覆盖 schema 自检、三个样例、置信度缺失/越界/非有限数、各词性连续编号、15 词限制、跨词性总义项审核、重复检测、例句配对与总数、来源绑定，以及 v2 被旧版 SQLite 入口拒绝。

## 后续集成边界

Phase 3 需要构建显式的原始数据到候选请求适配器，把可信元数据与模型生成字段分开；候选仍应通过本校验并保留审核报告。现有 `prepare_requests.py` / `apply_responses.py` 属于旧版 1.0 接口，不应拿来提交或导入 v2 数据。

独立审核应绑定候选内容哈希及来源版本；人工更改候选后原审核失效。审核结果与模型输出分开存储，再由专用导出适配器接入词典。当前阶段没有实现审核批准、全量生成、安装或发布。
