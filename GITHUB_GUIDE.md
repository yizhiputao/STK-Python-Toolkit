# 📤 GitHub 上传指南

## 快速开始（推荐）

### 方法一：使用自动化脚本（最简单）

1. 在GitHub上创建仓库（浏览器应该已打开）
2. 创建完成后，复制仓库URL
3. 运行脚本：
   ```powershell
   .\push_to_github.ps1
   ```
4. 按提示粘贴仓库URL，完成！

---

## 详细步骤

### 第一步：在GitHub上创建仓库

1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name**: `testpythonstk`
   - **Description**: `STK Python Toolkit - 用于与AGI STK11交互的Python工具包`
   - **Public** 或 **Private**（根据需要选择）
   - ⚠️ **不要勾选** "Add a README file"
   - ⚠️ **不要勾选** "Add .gitignore"
   - ⚠️ **不要勾选** "Choose a license"
3. 点击 **"Create repository"**

### 第二步：获取仓库URL

创建完成后，你会看到一个页面，上面有仓库的URL，有两种格式：

**HTTPS格式（推荐新手）：**
```
https://github.com/你的用户名/testpythonstk.git
```

**SSH格式（需要配置SSH密钥）：**
```
git@github.com:你的用户名/testpythonstk.git
```

### 第三步：推送代码

#### 选项A：使用脚本（推荐）

```powershell
.\push_to_github.ps1
```

#### 选项B：手动命令

```bash
# 1. 添加远程仓库
git remote add origin https://github.com/你的用户名/testpythonstk.git

# 2. 重命名分支为main（可选，GitHub默认分支）
git branch -M main

# 3. 推送代码
git push -u origin main
```

---

## 可能遇到的问题

### 问题1：Authentication failed（认证失败）

**原因**：GitHub从2021年8月起不再支持密码认证

**解决方案**：使用Personal Access Token (PAT)

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置：
   - Note: `testpythonstk-token`
   - Expiration: 选择过期时间
   - ✅ 勾选 `repo`（完整的仓库权限）
4. 点击 "Generate token"
5. **立即复制token**（只显示一次！）
6. 推送时使用token作为密码：
   - 用户名：你的GitHub用户名
   - 密码：粘贴token（不是你的GitHub密码）

### 问题2：remote origin already exists（远程仓库已存在）

```bash
# 查看现有远程仓库
git remote -v

# 删除旧的
git remote remove origin

# 添加新的
git remote add origin https://github.com/你的用户名/testpythonstk.git
```

### 问题3：Updates were rejected（推送被拒绝）

```bash
# 先拉取远程更改
git pull origin main --allow-unrelated-histories

# 解决冲突（如果有）
# 然后再推送
git push -u origin main
```

### 问题4：网络问题

如果连接GitHub很慢或失败，可以尝试：

```bash
# 测试连接
ssh -T git@github.com

# 或配置代理（如果有）
git config --global http.proxy http://127.0.0.1:7890
```

---

## 后续使用

### 日常提交和推送

```bash
# 1. 修改代码后，添加到暂存区
git add .

# 2. 提交更改
git commit -m "描述你的更改"

# 3. 推送到GitHub
git push
```

### 查看状态

```bash
# 查看本地状态
git status

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline

# 查看远程分支
git branch -a
```

### 克隆到其他电脑

```bash
git clone https://github.com/你的用户名/testpythonstk.git
```

---

## SSH配置（可选，更方便）

### 生成SSH密钥

```bash
# 生成密钥（邮箱改成你的）
ssh-keygen -t ed25519 -C "1469264461@qq.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 添加到GitHub

1. 复制公钥内容
2. 访问：https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥，保存

### 测试连接

```bash
ssh -T git@github.com
```

成功后会显示：
```
Hi 你的用户名! You've successfully authenticated...
```

### 修改远程URL为SSH

```bash
git remote set-url origin git@github.com:你的用户名/testpythonstk.git
```

---

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 查看远程仓库 | `git remote -v` |
| 添加远程仓库 | `git remote add origin <URL>` |
| 修改远程URL | `git remote set-url origin <URL>` |
| 删除远程仓库 | `git remote remove origin` |
| 推送代码 | `git push` |
| 拉取代码 | `git pull` |
| 克隆仓库 | `git clone <URL>` |
| 查看分支 | `git branch -a` |
| 切换分支 | `git checkout <分支名>` |

---

## 更多资源

- GitHub官方文档：https://docs.github.com/zh
- Git教程：https://www.liaoxuefeng.com/wiki/896043488029600
- GitHub Desktop（图形化工具）：https://desktop.github.com/

---

祝你使用愉快！🚀

