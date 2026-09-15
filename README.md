# 维天说 · 全网资料搜索 Skill

> 让 AI 先去对的地方搜，再把结果整理成可核验的证据。

[![GitHub](https://img.shields.io/badge/GitHub-public-181717?logo=github)](https://github.com/zhoutian1995/weitian-research-skill)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

这是一个面向 Codex、Claude Code 等 Agent 的资料搜索 Skill。它根据**任务类型、地区和证据目标**选择平台，把“国内用户声音”“海外行业观点”“技术一手资料”“视频内容”分到不同的搜索路径，减少错搜和重复劳动。

## 适合谁

- 做国内电商、跨境、消费和内容行业调研
- 需要同时查抖音、B站、小红书、公众号、X、Reddit、YouTube
- 想把视频快速变成带时间戳的文字证据
- 希望每条结论都能回到来源，而不是只得到一段没有出处的摘要

## 它怎么分流

| 你的问题 | 优先来源 | 主要产出 |
| --- | --- | --- |
| 国内用户痛点、购买理由、实操经验 | 抖音、B站、小红书 | 用户声音、候选内容、互动信号 |
| 国内政策、规则、行业案例 | 公众号公开文章、官方页面 | 一手正文、发布日期、规则依据 |
| 海外市场、竞品和实时观点 | X（Twitter）、Reddit、YouTube、网页 | 观点、讨论串、视频和链接 |
| 技术实现、API、开源项目 | 官方文档、GitHub、论文、技术社区 | 版本、代码、限制和可复现实验 |
| 视频资料 | 平台字幕或 Windows GPU 转写 | JSON、Markdown、SRT、时间戳 |

GitHub 不会作为国内电商用户声音的默认来源；只有技术问题明确需要时才启用。

## 推荐工作方式

把一个大任务拆成独立会话，每个会话只做一件事：

1. **发现**：快速扫平台，建立候选清单。
2. **核验**：补作者、时间、原始链接和一手资料。
3. **转写**：只处理已经选中的视频。
4. **综合**：区分事实、用户原话和分析判断。

会话之间交接结构化清单和证据文件，不交接 Cookie、临时页面状态或高权限操作。

## 安装和自检

下载或克隆仓库后，复制整个 `skills/research-router/` 目录；只复制 `SKILL.md` 会缺少脚本和上游运行时。

先运行跨平台环境诊断：

```bash
python3 scripts/环境诊断.py
```

诊断是只读的，不读取 Cookie，也不上传系统信息：

- Windows：检查 NVIDIA GPU、`nvidia-smi`、CUDA 可见性、ffmpeg 和 faster-whisper。
- macOS：检查芯片、内存、本地浏览器会话条件、ffmpeg 和外接 SSD。

## 四个常见例子

### 1. 国内电商用户痛点

```bash
python3 scripts/资料搜索.py "跨境电商卖家最常见的售后问题" \
  --task pain_points --region domestic --dry-run
```

命令会生成 Ego Lite 的分平台任务清单；登录平台由用户在独立浏览器会话中完成。

### 2. 海外竞品和市场观点

```bash
python3 skills/research-router/scripts/资料搜索.py \
  "cross-border returns software competitors" \
  --task competitor --region overseas --speed fast --run
```

没有 X 授权时，结果会明确标记 `requires_explicit_auth`，不会把“无法访问”写成“没有讨论”。

### 3. 技术资料核验

```bash
python3 skills/research-router/scripts/资料搜索.py \
  "faster-whisper CUDA quantization deployment" \
  --task technical --region global --speed fast --dry-run
```

技术路由才会考虑 GitHub、官方文档、论文和 issue。

### 4. 视频转写

先选定少量重点视频，再把文件放到外接 SSD，在 Windows RTX GPU 上运行：

```powershell
.\scripts\transcribe-windows.ps1 "E:\WilleSpace-Work\KnowledgeBase\10-raw\待转写\video.mp4"
```

默认使用 `large-v3-turbo`，输出词级时间戳 JSON、可读 Markdown 和 SRT。详见 [Windows 转写说明](Windows转写说明.md)。

## 输出和证据规范

每条证据尽量包含：

```text
platform · title · author · published_at · engagement · url
 evidence_type · status
```

缺少字段会标记为 `partial`，不会猜测补齐。常见状态包括：`no-results`、`requires_login`、`requires_explicit_auth`、`rate-limited`、`unreachable`。

统一字段可用：

```bash
python3 scripts/证据规范化.py raw.json --platform xiaohongshu
```

## 速度和限制

- 国内路由清单生成约 0.03–0.04 秒；实际页面速度由 Ego Lite、网络和登录态决定。
- 抖音、B站、小红书页面采集约 3 秒级；小红书保持低频人工确认。
- 海外公开聚合实测从几秒到约 80 秒都有可能，不能当作稳定 SLA。
- Windows RTX 5070 中文视频转写实测约 48 倍实时。

默认使用 `fast`，确认主题后再进入 `balanced` 或 `deep`。BibiGPT 和平台 API 暂不作为默认依赖；只有在高频批量、稳定分页或结构化抽取持续失败时才评估付费 API。

## 安全边界

- 只读：不点赞、不评论、不关注、不发布。
- 不做验证码对抗、指纹伪装、Cookie 导出或批量视觉爬取。
- 运行数据、视频和转写结果写入外接 SSD KnowledgeBase；SSD 不可用时停止。
- 不要把 Cookie、API key、个人数据或私密资料提交到仓库。

## 目录

```text
skills/research-router/       可安装 Skill、路由脚本和上游运行时
scripts/                      兼容旧命令的入口
平台路由.yaml                 机器可读的平台与会话路由
目标与验收标准.md              项目目标和验收条件
NOTICE.md                     上游归属与发布说明
assets/contact/               微信联系和公众号二维码
```

## 联系

微信联系：

![微信联系二维码](assets/contact/wechat-contact.jpg)

公众号：

![公众号二维码](assets/contact/wechat-official-account.webp)

## 上游和许可证

本项目采用 [MIT License](LICENSE)。海外聚合运行时基于 [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)，上游许可文本保留在 `skills/research-router/vendor/LICENSE`；详细归属见 [NOTICE.md](NOTICE.md)。

欢迎通过 Issue 提交平台适配、证据字段或安全边界方面的改进建议。

## 微信公众号搜索

国内行业和案例研究已纳入公众号：在 Ego Lite 中通过搜狗微信发现候选，再打开公众号原文核对作者、正文和日期。备用入口为公开网页搜索和用户提供的文章链接。详细流程见 [公众号搜索与正文核验](skills/research-router/references/公众号搜索与正文核验.md)。

已完成一次单篇浏览器链路验证，搜索页约 9 秒；全文完整性、签名链接长期有效性及多主题稳定性仍需继续验证。当前脚本生成搜索计划，浏览器负责实际检索，不是全自动批量采集器。证据整理支持单篇记录，并保留搜索页日期、可见正文和缺失说明；厂商宣传与用户实际经历分别标注。
