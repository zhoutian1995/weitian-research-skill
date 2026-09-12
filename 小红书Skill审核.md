# 小红书 Skill / 项目审核（2026-09-12）

本清单只记录公开 GitHub 审查结果和隔离副本审计。候选项目不会直接进入主仓库。

## 候选对比

| 项目 | Star / Fork | 主要能力 | 账号与风控面 | 当前决定 |
|---|---:|---|---|---|
| [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) | 64,859 / 12,584 | 多平台搜索、笔记、作者和评论采集；支持 XHS CDP | 复用本地 Chrome/Edge 登录态；可配置代理和评论抓取；无明确 SPDX 许可证 | **候选第一**，先做本地 CDP 只读改造和最小测试 |
| [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) | 15,749 / 2,315 | MCP 搜索、详情、评论、发布、点赞、收藏 | 本地 Cookie、登录态、代理配置；写操作齐全 | **暂不原样接入**，只考虑抽取只读搜索和详情 |
| [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 79,542 / 6,860 | 多平台路由，XHS 可接 OpenCLI / MCP / CLI | 自身强调 Cookie 本地保存，但会引导接入需要登录的后端 | **暂不安装**，可作为路由设计参考 |
| [jackwener/xiaohongshu-cli](https://github.com/jackwener/xiaohongshu-cli) | 2,585 / 269 | 搜索、详情、评论、互动、发布 | 逆向 API、自动提取浏览器 Cookie、反检测、验证码退避 | **不接入主账号**；风险面超出本项目需要 |
| [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills) | 3,419 / 343 | CDP 发布、搜索、详情、评论、数据看板 | 多账号 Cookie、无头模式、发布和互动；仓库自身提示封号风险 | **不接入**，发布能力与资料搜索无关 |
| [Xiangyu-CAS/xiaohongshu-ops-skill](https://github.com/Xiangyu-CAS/xiaohongshu-ops-skill) | 2,339 / 249 | 账号分析、推荐流、选题、发布和复刻 | CDP 登录、自动发布/回复 | **不接入**，运营写操作过多 |
| [JoeanAmier/XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) | 12,676 / 1,864 | 选中链接后的作品信息和媒体下载 | 自动滚动和账号作品功能可能触发风控；GPL-3.0 | **仅作后处理备选**，不做批量发现 |
| [cv-cat/Spider_XHS](https://github.com/cv-cat/Spider_XHS) | 7,640 / 1,313 | PC/创作者/蒲公英场景采集 | 同时包含发布、私信、点赞等写 API；许可证不明 | **不接入** |

Star 只代表项目关注度，不代表封号安全、数据准确或维护质量。上表数值来自 GitHub API 检索当日快照，后续会变化。

MediaCrawler 已以浅克隆形式放在 `/Users/wille/projects/xhs-mediacrawler`，只做了静态审核，没有安装依赖或启动。它的许可证是非商业学习许可（GitHub API 无标准 SPDX 标识），而且包含代理池、隐身脚本、评论抓取和 Cookie 登录路径；因此**不把源码并入资料搜索主仓库，也不用于商业生产链路**。如需技术验证，只能另建只读适配器并先核对许可证边界。

MediaCrawler 的 CDP 模式还需要验证 Ego Lite 是否提供兼容的远程调试接口，不能直接假设可用。在验证前，默认继续使用 Ego Lite 的低频人工只读会话。

## 只读改造方案

如果继续推进，单独建立 `xhs-readonly-adapter`，只保留：

- 关键词搜索笔记；
- 笔记详情、作者、发布时间和公开互动指标；
- 明确的 `requires_login`、`rate-limited`、`unreachable` 状态；
- 每轮少量请求和人工确认。

必须删除或禁用：

- 发布、点赞、收藏、评论、回复、关注和删除；
- Cookie 自动提取、Cookie 导出和跨浏览器扫描；
- 代理池、验证码绕过、伪装指纹和高频翻页；
- 自动下载全量图片/视频。

## 结论

当前最稳方案仍是 Ego Lite 低频人工只读搜索。第三方项目即使 Star 很高，也只能先做静态审核，再在隔离环境中验证只读子集；不把完整项目直接放进主账号环境。
