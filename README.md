# 维天说｜全网资料搜索 Skill

一个按**任务、地区和证据类型**自动分流的资料搜索工作台，解决“国内电商问题却跑去 GitHub 搜”的常见误路由。

> 当前版本已经提交并公开发布：<https://github.com/zhoutian1995/weitian-research-skill>

## 它解决什么问题

- 国内电商、消费和创作者话题：优先抖音、B站、小红书、公众号。
- 海外市场和行业观点：优先 X（Twitter）、Reddit、YouTube 和网页。
- 技术问题：只有明确属于技术求证时，才启用官方文档、GitHub、论文和技术社区。
- 视频资料：先拿到候选链接，再交给 Windows RTX 5070 + faster-whisper 转写。
- 所有结果统一为带来源、作者、时间、互动量、链接和状态的证据记录。

它不做点赞、评论、关注、发布，也不导出 Cookie；小红书采用低频、公开页面或人工登录的 Ego Lite 会话。

## 会话怎么拆

| 会话 | 主要来源 | 输出 |
| --- | --- | --- |
| 国内电商发现 | 抖音、B站、小红书 | 候选清单和用户声音 |
| 国内电商核验 | 公众号、规则页、详情页 | 可追溯正文和一手证据 |
| 海外市场研究 | X、Reddit、YouTube、网页 | 海外观点和讨论证据 |
| 技术资料核验 | 官方文档、GitHub、论文 | API、实现和事实核验 |
| 视频转写 | Windows RTX 5070 | JSON、Markdown、SRT 和时间戳 |

会话之间只交接结构化候选清单和证据文件，不交接 Cookie 或临时页面状态。

## 快速开始

复制整个 `skills/research-router/` 目录，不能只复制 `SKILL.md`。

国内路由（只生成 Ego Lite 任务清单，不联网）：

```bash
python3 scripts/资料搜索.py "1688 电商痛点" --task pain_points --region domestic --dry-run
```

海外快速发现：

```bash
python3 skills/research-router/scripts/资料搜索.py "cross-border ecommerce pain points" \
  --task pain_points --region overseas --speed fast --run
```

运行环境：国内路由在 Python 3.9+ 已验证；海外和技术路由需要 Python 3.12+。Windows 转写需要 CUDA、faster-whisper 和外接 SSD KnowledgeBase，见 [Windows转写说明.md](Windows转写说明.md)。

## 速度和真实边界

- 国内路由清单生成：约 0.03–0.04 秒。
- Ego Lite 抖音、B站、小红书页面采集：约 3 秒级，受登录态和页面加载影响。
- 海外 fast：实测约 4.6 秒和 79.2 秒，公开源响应和退避会造成明显波动。
- RTX 5070 转写：中文视频实测约 48 倍实时。

因此默认先 fast，再对少量重点来源进入 balanced/deep；不会为了“全平台”每次都等待视频字幕和评论。

## 安全和合规边界

- 小红书、抖音、B站只读，低频、人工确认；不做验证码对抗、指纹伪装或批量视觉爬取。
- X 没有显式授权时标记为 `requires_explicit_auth`，不会把未授权误报为“没有讨论”。
- 下载、转写和运行产物写入外接 SSD KnowledgeBase；SSD 不可用时停止，不回退到 NAS 或内置盘。
- 不要把登录 Cookie、API key、个人数据或私密资料提交到仓库。

## 目录

- `skills/research-router/`：可安装 Skill、脚本和经过审核的上游运行时。
- `scripts/`：兼容旧命令的薄包装。
- `平台路由.yaml`：机器可读的平台和会话路由。
- `目标与验收标准.md`：项目目标、验收条件和未完成项。
- `NOTICE.md`：上游项目归属和公开发布说明。
- `assets/contact/wechat-contact.jpg`：微信联系二维码。

## 联系周老师

微信联系：

![微信联系二维码](assets/contact/wechat-contact.jpg)

公众号：

![公众号二维码](assets/contact/wechat-official-account.webp)

## 许可证

本项目采用 MIT License。上游 `last30days-skill` 的版权和 MIT 文本保留在 `skills/research-router/vendor/LICENSE`；详见 [NOTICE.md](NOTICE.md)。
