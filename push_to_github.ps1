# 推送项目到GitHub的脚本
# 使用方法: .\push_to_github.ps1

# 检查是否在Git仓库中
if (-not (Test-Path ".git")) {
    Write-Host "错误: 当前目录不是Git仓库。" -ForegroundColor Red
    exit 1
}

# 获取GitHub仓库URL
Write-Host "请输入你的GitHub仓库URL" -ForegroundColor Yellow
Write-Host "格式示例: https://github.com/你的用户名/testpythonstk.git" -ForegroundColor Gray
Write-Host "或SSH格式: git@github.com:你的用户名/testpythonstk.git" -ForegroundColor Gray
Write-Host ""
Write-Host "GitHub仓库URL: " -NoNewline -ForegroundColor Green
$repoUrl = Read-Host

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "错误: 未输入仓库URL。" -ForegroundColor Red
    exit 1
}

# 检查是否已经添加了remote
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host ""
    Write-Host "警告: 已存在远程仓库 'origin': $existingRemote" -ForegroundColor Yellow
    Write-Host "是否要更新为新的URL? (Y/N): " -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "正在更新远程仓库URL..." -ForegroundColor Cyan
        git remote set-url origin $repoUrl
    } else {
        Write-Host "保持原有远程仓库配置。" -ForegroundColor Green
    }
} else {
    # 添加远程仓库
    Write-Host ""
    Write-Host "正在添加远程仓库..." -ForegroundColor Cyan
    git remote add origin $repoUrl
}

# 显示远程仓库信息
Write-Host ""
Write-Host "当前远程仓库配置:" -ForegroundColor Cyan
git remote -v

# 检查当前分支
$currentBranch = git branch --show-current
Write-Host ""
Write-Host "当前分支: $currentBranch" -ForegroundColor Cyan

# 询问是否要重命名分支为main（GitHub默认）
if ($currentBranch -eq "master") {
    Write-Host ""
    Write-Host "GitHub现在默认使用'main'作为主分支名。" -ForegroundColor Yellow
    Write-Host "是否将当前分支从'master'重命名为'main'? (Y/N): " -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "正在重命名分支..." -ForegroundColor Cyan
        git branch -M main
        $currentBranch = "main"
    }
}

# 推送到GitHub
Write-Host ""
Write-Host "准备推送代码到GitHub..." -ForegroundColor Green
Write-Host "是否现在推送? (Y/N): " -NoNewline
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "正在推送到 origin/$currentBranch ..." -ForegroundColor Cyan
    git push -u origin $currentBranch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   成功推送到 GitHub！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "你的项目已经上传到GitHub了！" -ForegroundColor Green
        Write-Host "可以访问你的仓库查看代码。" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "推送失败。可能的原因:" -ForegroundColor Red
        Write-Host "1. 仓库URL不正确" -ForegroundColor Yellow
        Write-Host "2. 没有权限（需要配置SSH密钥或使用Personal Access Token）" -ForegroundColor Yellow
        Write-Host "3. 网络问题" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "如需帮助，请查看 GitHub 文档或运行: git push --help" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "已取消推送。你可以稍后手动推送:" -ForegroundColor Yellow
    Write-Host "  git push -u origin $currentBranch" -ForegroundColor Cyan
}

Write-Host ""

