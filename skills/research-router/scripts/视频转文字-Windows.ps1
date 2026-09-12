param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputPath,
    [Parameter(ValueFromRemainingArguments = $true, Position = 1)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"
$workRoot = if ($env:WILLE_WORK_ROOT) { $env:WILLE_WORK_ROOT } else { "E:\WilleSpace-Work" }
$repoRoot = $PSScriptRoot

if (-not (Test-Path -LiteralPath (Join-Path $workRoot ".wille-work-storage"))) {
    throw "未找到外接 SSD 存储哨兵：$workRoot\.wille-work-storage"
}
$knowledgeBase = Join-Path $workRoot "KnowledgeBase"
if (-not (Test-Path -LiteralPath $knowledgeBase -PathType Container)) {
    throw "未找到 KnowledgeBase：$knowledgeBase"
}

# Reuse the already benchmarked environment when this repository is copied to E:.
$candidates = @(
    (Join-Path $workRoot "projects\xiaoe-course-archive\.venv\Scripts\python.exe"),
    (Join-Path $workRoot "projects\weitian-research-skill\.venv\Scripts\python.exe"),
    (Join-Path $repoRoot ".venv\Scripts\python.exe")
)
$python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) {
    throw "找不到 Python 环境。请先按 Windows转写说明.md 创建 .venv 并安装 requirements-windows.txt。"
}

# ctranslate2's CUDA wheels ship their DLLs inside the venv; Windows does not
# always search these directories automatically.
$sitePackages = Join-Path (Split-Path -Parent (Split-Path -Parent $python)) "Lib\site-packages"
$cudaBins = Get-ChildItem -LiteralPath (Join-Path $sitePackages "nvidia") -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName "bin" } |
    Where-Object { Test-Path -LiteralPath $_ }
if ($cudaBins) {
    $env:PATH = (($cudaBins -join ";") + ";" + $env:PATH)
}

$env:WILLE_WORK_ROOT = $workRoot
$defaultCache = Join-Path $workRoot "caches\huggingface\hub"
if (-not (Test-Path -LiteralPath $defaultCache -PathType Container)) {
    $defaultCache = Join-Path $workRoot "models\faster-whisper"
}
$env:FASTER_WHISPER_CACHE = if ($env:FASTER_WHISPER_CACHE) { $env:FASTER_WHISPER_CACHE } else { $defaultCache }
$env:FASTER_WHISPER_MODEL = if ($env:FASTER_WHISPER_MODEL) { $env:FASTER_WHISPER_MODEL } else { "large-v3-turbo" }
$env:FASTER_WHISPER_DEVICE = if ($env:FASTER_WHISPER_DEVICE) { $env:FASTER_WHISPER_DEVICE } else { "cuda" }
$env:FASTER_WHISPER_COMPUTE_TYPE = if ($env:FASTER_WHISPER_COMPUTE_TYPE) { $env:FASTER_WHISPER_COMPUTE_TYPE } else { "float16" }

$script = Join-Path $repoRoot "transcribe.py"
& $python $script $InputPath @ExtraArgs
exit $LASTEXITCODE
