# Git 仓库初始化脚本
# 用法: .\init_git.ps1

Write-Host "正在初始化Git仓库..." -ForegroundColor Green

# 检查Git是否可用
try {
    git --version
} catch {
    Write-Host "错误: Git未找到。请确保Git已安装并重启PowerShell。" -ForegroundColor Red
    exit 1
}

# 检查是否已经是Git仓库
if (Test-Path ".git") {
    Write-Host "警告: 当前目录已经是Git仓库。" -ForegroundColor Yellow
    exit 0
}

# 初始化Git仓库
Write-Host "1. 初始化Git仓库..." -ForegroundColor Cyan
git init

# 配置用户信息（可选，根据需要修改）
Write-Host "2. 配置Git用户信息..." -ForegroundColor Cyan
Write-Host "   请输入你的Git用户名（按回车跳过）: " -NoNewline
$userName = Read-Host
if ($userName) {
    git config user.name "$userName"
}

Write-Host "   请输入你的Git邮箱（按回车跳过）: " -NoNewline
$userEmail = Read-Host
if ($userEmail) {
    git config user.email "$userEmail"
}

# 添加所有文件到暂存区
Write-Host "3. 添加文件到暂存区..." -ForegroundColor Cyan
git add .

# 查看状态
Write-Host "4. 当前Git状态:" -ForegroundColor Cyan
git status

# 创建初始提交
Write-Host "`n5. 是否创建初始提交? (Y/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    git commit -m "Initial commit: STK Toolkit Python project"
    Write-Host "`nGit仓库初始化完成！" -ForegroundColor Green
    Write-Host "你可以使用以下命令管理你的代码:" -ForegroundColor Cyan
    Write-Host "  git status       - 查看仓库状态"
    Write-Host "  git add <file>   - 添加文件到暂存区"
    Write-Host "  git commit -m 'message' - 提交更改"
    Write-Host "  git log          - 查看提交历史"
} else {
    Write-Host "`nGit仓库已初始化，但未创建提交。" -ForegroundColor Yellow
    Write-Host "你可以稍后使用 'git commit -m ""message""' 创建提交。"
}

