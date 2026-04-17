# VA皮肤科小红书自动运营 Skill

## 快速开始

### 1. 环境准备

```bash
# 设置环境变量
export XHS_VERSION=intl
export XHS_USER_DATA_DIR=/Users/macstudio/.xhs/chrome-profile-intl

# 确保Chrome在后台运行
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/Users/macstudio/.xhs/chrome-profile-intl \
  --disable-blink-features=AutomationControlled \
  --lang=zh-CN
```

### 2. 登录

```bash
python3 scripts/cli.py login
# 扫码登录后保持Chrome运行
```

### 3. 开始自动评论

```bash
python3 scripts/simple_stable_comment.py
```

---

## 功能特性

- ✅ 主页推荐浏览 + 关键词搜索双渠道
- ✅ 自动评论（54条话术随机选取）
- ✅ 自动点赞（30%概率）
- ✅ 自动收藏（20%概率）
- ✅ 智能去重（不重复评论）
- ✅ 时间过滤（只评论30天内）
- ✅ 内容相关性检测
- ✅ 机构号过滤
- ✅ 竞品黑名单

---

## 核心卖点

1. **园长大教授·从业20+年** - 梨大大教授级院长，资历深厚
2. **梨大仪器库·项目最全** - 一站式搞定，不用跑多家
3. **白菜价·高性价比** - 大教授级别但价格亲民

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 完整规则文档 |
| `scripts/simple_stable_comment.py` | 主执行脚本 |
| `config/keywords.txt` | 搜索关键词列表 |
| `docs/comments.md` | 评论话术完整版 |
| `docs/rules.md` | 过滤规则详细说明 |

---

## 注意事项

1. 只使用 `simple_stable_comment.py`，不要使用 `auto_comment.py`（已废弃）
2. 保持Chrome在后台运行
3. 如果提示"已评论过"过多，检查记录文件
4. 登录状态失效时需重新扫码登录

---

## 目录结构

```
xiaohongshu-jd-skill/
├── SKILL.md                    # 完整规则文档
├── README.md                   # 本文件
├── scripts/
│   └── simple_stable_comment.py # 主执行脚本
├── config/
│   └── keywords.txt            # 搜索关键词
└── docs/
    ├── comments.md             # 评论话术
    └── rules.md                # 过滤规则
```
