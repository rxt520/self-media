# Prompt Template

## Direct Use Prompt

```text
请使用这个本地技能目录作为唯一主入口：
C:\custom\project1\ideas\self-media\skills\script-writing\口播生成复用技能

开始前请先读取：
1. SKILL.md
2. rule-pack.md
3. review-roles.md
4. risk-control.md
5. scoring-loop.md

任务：
围绕“想做自媒体，并希望用 AI 辅助提效和提升关注度的真人口播博主”生成抖音真人口播脚本。

要求：
- 一条脚本只讲 1 个根问题
- 优先从 AI 剪辑提效、账号聚焦、稳定输出 3 个切口里选
- 主标题不超过 10 个字，带副标题
- 按 1.5 分钟完整版生成
- 必须有至少 1 个硬证明锚点
- AI 只能写成辅助提效，不能替代人判断
- 结尾优先用“陈述式后续线索 + 收藏型 CTA”

审核要求：
- 先做结构审核
- 再做抖音风控审核
- 再做 12 个用户角色审核
- 最后做评分审核
- 不通过就指出具体坏掉的规则并回炉重写

最终只交付正式过线版本。
```

## Batch Prompt

```text
请基于本地技能目录批量生成 6 条脚本：
C:\custom\project1\ideas\self-media\skills\script-writing\口播生成复用技能

同一核心人群下做 6 个不同选题。
每条都必须经过：
1. 结构审核
2. 风控审核
3. 12 角色审核
4. 评分审核

过线标准：
- 结构 pass
- 风控 pass
- 12 角色里至少 8 个正向
- 评分至少 82/100

不达标就继续重写，直到交付正式可用版本。
```
