# sync.ps1 - 一键提交推送（含安全自查）
param([string]$message = "update")

# 安全自查：检查是否有敏感文件被跟踪
$sensitive = git status --porcelain | Select-String -Pattern "\.env|config\.json|\.key"
if ($sensitive) {
    Write-Host "警告：检测到敏感文件被跟踪！" -ForegroundColor Red
    git status --porcelain
    exit 1
}

git add .

# 判断是否有变更（用退出码判断，修正原逻辑反了的问题）
git diff --cached --quiet
if ($LASTEXITCODE -eq 1) {
    git commit -m $message
    if ($LASTEXITCODE -ne 0) {
        Write-Host "提交失败！请检查 git 身份配置" -ForegroundColor Red
        exit 1
    }
    git push
    if ($LASTEXITCODE -ne 0) {
        Write-Host "推送失败！请检查网络/代理/认证" -ForegroundColor Red
        exit 1
    }
    Write-Host "提交并推送成功: $message" -ForegroundColor Green
} else {
    Write-Host "没有变更需要提交" -ForegroundColor Yellow
}