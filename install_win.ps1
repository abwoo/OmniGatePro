# OmniGate Pro - Windows 全局环境注册脚本
$currentDir = Get-Location
$binDir = "$HOME\.omnigate\bin"

if (!(Test-Path $binDir)) {
    New-Item -ItemType Directory -Force -Path $binDir
}

# 创建启动快捷批处理
$batContent = "@echo off`npython ""$currentDir\cli.py"" %*"
$batContent | Out-File -FilePath "$binDir\omni.bat" -Encoding ascii

# 将路径添加到用户 PATH（如果不存在）
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
    Write-Host "✅ 已将 OmniGate 注册到系统 PATH。" -ForegroundColor Green
    Write-Host "🚀 请【重启终端】后，直接输入 'omni' 即可使用！" -ForegroundColor Cyan
} else {
    Write-Host "ℹ️ PATH 已配置，无需重复操作。" -ForegroundColor Yellow
}
