# Windows RTX 5070 转写说明

## 目标

视频先由 Ego Lite 或授权下载流程取得本地文件，再在 Windows RTX 5070 上用 faster-whisper 本地转写。视频、JSON、Markdown、SRT 和模型缓存都放在 E 盘工作区，不上传 BibiGPT，也不读取平台 Cookie。

## 一次性准备

在 Windows PowerShell 中确认以下目录存在：

```text
E:\WilleSpace-Work\
E:\WilleSpace-Work\.wille-work-storage
E:\WilleSpace-Work\KnowledgeBase\
```

仓库提供的启动脚本会优先复用已经验证过的小鹅课程环境，并自动补齐 CUDA DLL 搜索路径：

```powershell
.\scripts\transcribe-windows.ps1 "E:\WilleSpace-Work\KnowledgeBase\10-raw\social-media\待转写\视频.mp4"
```

仓库同时保留中文脚本名；Windows 启动时优先使用 ASCII 文件名，避免旧版 PowerShell 的代码页把中文路径解析成乱码。

如果环境尚未安装 faster-whisper，再安装 Python 依赖：

```powershell
py -3 -m venv E:\WilleSpace-Work\projects\weitian-research-skill\.venv
E:\WilleSpace-Work\projects\weitian-research-skill\.venv\Scripts\python.exe -m pip install -U pip
E:\WilleSpace-Work\projects\weitian-research-skill\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
```

首次运行会把模型下载到 `E:\WilleSpace-Work\models\faster-whisper`。默认模型为已经在 RTX 5070 上验证过的 `large-v3-turbo`；需要更高准确率时可传 `--model large-v3`。

## 运行

```powershell
python scripts\视频转文字.py "E:\WilleSpace-Work\KnowledgeBase\10-raw\social-media\待转写\视频.mp4"
```

输出目录默认为：

```text
E:\WilleSpace-Work\KnowledgeBase\10-raw\social-media\transcripts\
```

脚本生成带词级时间戳的 JSON、可阅读 Markdown 和 SRT。输出目录不在 KnowledgeBase 下时会拒绝执行。

## 注意

- 当前 Windows 主机尚未安装 `yt-dlp`，因此本脚本只处理本地文件。
- 5070 实测：5191 秒中文视频使用 `large-v3-turbo`、FP16 约 108.7 秒（约 47.8 倍实时）。
- 如果显卡驱动或 CUDA 运行库不匹配，设置 `FASTER_WHISPER_DEVICE=cpu` 只能用于故障诊断，正式转写不要走 CPU。
- BibiGPT 只作为未来可选云端后端，本仓库当前不调用它。
