# 小红书自动运营 Skill

自动在小红书（RedNote 国际版）上评论韩国医美相关帖子，支持任意诊所配置。

---

## 系统要求

| 要求 | 说明 |
|------|------|
| 操作系统 | macOS / Windows 10+ / Linux |
| Python | **3.11 或更高版本** |
| Chrome | 最新版 Google Chrome |
| 网络 | 能正常访问 rednote.com |

---

## 安装步骤

### 第一步：下载本仓库

```bash
git clone https://github.com/gaojiongwenv587-beep/xiaohongshu-jd-skill.git
cd xiaohongshu-jd-skill
```

### 第二步：安装 Python 依赖

```bash
pip install -r requirements.txt
```

> 如果 `pip` 命令报错，尝试 `pip3 install -r requirements.txt`

### 第三步：配置诊所信息（首次运行时自动触发）

直接运行主脚本，首次运行会自动启动配置向导：

```bash
python scripts/simple_stable_comment.py
```

向导会询问：
- 诊所名称（如：VA、曙光医院）
- 所在地区（如：梨大、江南、新沙）
- 医生职称（如：大教授、主任医师）
- 负责人称谓（如：园长、院长）

配置保存在 `config/clinic.json`，之后运行不再询问。

### 第四步：登录小红书

脚本运行时会自动打开 Chrome 并提示扫码登录。
登录成功后保持 Chrome 在后台运行即可。

---

## 日常使用

每次运行：

```bash
python scripts/simple_stable_comment.py
```

脚本自动完成：主页浏览 → 关键词搜索 → 过滤 → 评论/点赞/收藏

---

## Windows 用户

直接在命令提示符（CMD）或 PowerShell 运行：

```cmd
python scripts\simple_stable_comment.py
```

> Chrome 路径和用户数据目录会自动检测，无需手动配置。

---

## 重新配置诊所

删除配置文件后重新运行即可：

```bash
# macOS / Linux
rm config/clinic.json

# Windows
del config\clinic.json
```

---

## 常见问题

**Q：运行提示"找不到 Chrome"**
A：安装 Google Chrome：https://www.google.com/chrome/

**Q：运行提示"缺少 Python 包"**
A：运行 `pip install -r requirements.txt`

**Q：登录后提示"未登录"**
A：确保 Chrome 保持在后台运行，重新扫码登录

**Q：提示"已评论过"太多**
A：正常现象，说明去重机制生效。等待新帖子出现即可

---

## 功能特性

- 主页推荐 + 关键词搜索双渠道
- 自动评论（62 条话术随机选取）
- 自动点赞（30% 概率）
- 自动收藏（20% 概率）
- 智能去重，不重复评论
- 只评论 30 天内的帖子
- 机构号过滤 + 竞品黑名单
- 支持任意诊所配置

---

## 目录结构

```
xiaohongshu-jd-skill/
├── README.md                        # 本文件
├── SKILL.md                         # 完整规则文档（供 Claude 读取）
├── requirements.txt                 # Python 依赖
├── config/
│   ├── clinic.json                  # 诊所配置（运行后自动生成）
│   └── keywords.txt                 # 搜索关键词列表
├── scripts/
│   ├── simple_stable_comment.py     # 主执行脚本
│   ├── cli.py                       # XHS CLI 入口
│   ├── chrome_launcher.py           # Chrome 启动模块
│   ├── account_manager.py           # 账号管理
│   └── xhs/                         # XHS API 实现包
└── docs/
    ├── comments.md                  # 评论话术说明
    └── rules.md                     # 过滤规则说明
```
