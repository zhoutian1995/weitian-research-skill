# 资料搜索工作台

这是周老师的多平台资料搜索仓库。它把搜索任务按来源分流，避免把国内电商问题错误地交给 GitHub：

项目目标和验收标准见 [目标与验收标准.md](目标与验收标准.md)。

所有外部 Skill 必须先下载到 `~/projects`，经过只读审计和隔离冒烟测试，再决定是否改造和接入。流程见 [SKILL引入审核.md](SKILL引入审核.md)。

小红书候选项目的审核结果见 [小红书Skill审核.md](小红书Skill审核.md)。

- 国内电商：Ego Lite 搜抖音、B站和需要登录的公众号页面；公开公众号文章优先走网页，小红书保持低频、人工确认。
- 海外观点：last30days 聚合 **X（Twitter）**、Reddit、YouTube 和网页。
- 技术资料：只有用户明确要求时才搜索 GitHub、论文和官方文档。
- 视频：后续在 Windows RTX 5070 上用 faster-whisper 转写，媒体和转写结果落到外接 SSD KnowledgeBase。
- BibiGPT：暂记为未来可选云端后端，当前不接入、不购买会员。

## 当前组成

`skills/research-router/vendor/` 是审计过的上游源码快照，来源为 [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)。

`skills/research-router/SKILL.md` 是可安装的 Skill 入口；配套脚本和上游快照都在同一 Skill 目录内。仓库根目录的 `scripts/` 只保留向后兼容的薄包装，`scripts/资料搜索.py` 仍可生成任务清单并调用上游引擎处理海外来源。

安装时请复制整个 `skills/research-router/` 目录，不能只复制 `SKILL.md`。国内 Ego Lite 路由在本机 Python 3.9+ 已验证；海外/技术路由调用捆绑的 last30days runtime，需要 Python 3.12+。Windows 视频转写另需 Windows、CUDA 和 `faster-whisper`，详见 [Windows转写说明.md](Windows转写说明.md)。

任务清单会同时给出 `session_plan`：国内发现、国内核验、海外研究、技术核验和视频转写分别运行；会话之间只交接结构化候选清单和证据文件，不交接 Cookie 或临时页面状态。

`scripts/速度压测.py` 用于记录路由和公开搜索的耗时、返回码及平台状态。默认只测路由，不联网；加 `--run` 才会调用允许的上游公开来源。结果写入外接 SSD 的 `scratch/资料搜索`。

`scripts/证据规范化.py` 把 Ego Lite 或上游引擎导出的结果统一为 `platform/title/author/published_at/engagement/url/evidence_type/status` 字段；缺字段会标记为 `partial`，不会用猜测补齐。

视频转写使用 `scripts/视频转文字.py`；Windows 推荐调用 ASCII 文件名的 `scripts/transcribe-windows.ps1`，它会复用已验证的 5070 环境并自动补齐 CUDA DLL 路径。

## 使用

先查看路由，不会访问平台，也不会读取 Cookie：

```bash
python3 scripts/资料搜索.py "1688 电商痛点" --task pain_points --region domestic --dry-run
```

只运行海外公开来源：

```bash
python3 scripts/资料搜索.py "跨境电商履约痛点" --task pain_points --region overseas --speed fast --run
```

记录一次路由速度（不访问平台）：

```bash
python3 scripts/速度压测.py "1688 电商痛点" --task pain_points --region domestic --speeds fast balanced
```

需要 YouTube 视频、评论和字幕时再开第二阶段：

```bash
python3 scripts/资料搜索.py "跨境电商履约痛点" --task pain_points --region overseas --speed balanced --run
```

`fast` 是默认档位，优先快速判断；`balanced` 会加入 YouTube，速度通常会增加到 1～3 分钟，字幕缺失时还可能更久。

Windows 转写示例：

```powershell
.\scripts\transcribe-windows.ps1 "E:\WilleSpace-Work\KnowledgeBase\10-raw\social-media\待转写\视频.mp4"
```

`large-v3-turbo` 是默认模型；在 RTX 5070 上对 5191 秒中文视频实测约 109 秒（约 48 倍实时）。

脚本不会执行点赞、评论、关注、发布或批量抓取。小红书、抖音和 B 站的登录态搜索仍由独立 Ego Lite 会话人工完成。

## GitHub 发布说明

当前仓库是可审计的工作副本，尚未创建 commit 或 remote。公开发布前请阅读 [NOTICE.md](NOTICE.md)，选择仓库根目录的许可证，并决定是否保留约 33 MB 的上游测试夹具和媒体文件；建议先以 Private 仓库试运行。上游 last30days-skill 的 MIT 许可文件保留在 `skills/research-router/vendor/LICENSE`。
