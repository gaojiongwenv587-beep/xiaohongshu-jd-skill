#!/usr/bin/env python3
"""
小红书稳定版自动评论脚本 - RedNote 国际版适配
适配 rednote.com 国际版，搜索词和过滤词均针对海外用户习惯优化
"""
import os
import sys
import json
import time
import random
import socket
import subprocess
from datetime import datetime, timedelta

# ===== 平台检测 =====
IS_WINDOWS = sys.platform == 'win32'
IS_MAC     = sys.platform == 'darwin'

def _default_profile_dir():
    if IS_WINDOWS:
        base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        return os.path.join(base, 'xhs', 'chrome-profile-intl')
    return os.path.join(os.path.expanduser('~'), '.xhs', 'chrome-profile-intl')

def _chrome_exe():
    if IS_WINDOWS:
        for p in [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Google\Chrome\Application\chrome.exe'),
        ]:
            if os.path.exists(p):
                return p
        return 'chrome'          # 希望在 PATH 里
    if IS_MAC:
        return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    return 'google-chrome'       # Linux

# 设置海外版 RedNote 环境变量
if 'XHS_VERSION' not in os.environ:
    os.environ['XHS_VERSION'] = 'intl'
if 'XHS_USER_DATA_DIR' not in os.environ:
    os.environ['XHS_USER_DATA_DIR'] = _default_profile_dir()

# 已评论记录文件
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COMMENTED_FILE = os.path.join(SCRIPT_DIR, '.workbuddy', 'commented_feeds.json')

# 诊所配置文件
CONFIG_FILE = os.path.join(SCRIPT_DIR, '..', 'config', 'clinic.json')

# ===== 评论模板池（{clinic}=诊所名, {location}=地区, {title}=医生职称, {role}=负责人称谓）=====
COMMENT_TEMPLATES = [
    # ── 园长/大教授 20+年 ──
    "我们家{role}{location}{title}，从业二十多年了，找{clinic}放心",
    "{title}亲咨询不是说说，{clinic}{role}资历真的摆在那",
    "二十几年的{title}坐诊，{clinic}这个价格真的不贵",
    "{clinic}{role}教授级别的，不是随便挂个名那种",
    "{location}{title}出身，{clinic}{role}手上案例多到你想象不到",
    "找了好久，{clinic}{role}二十多年经验这个真没话说",
    "{title}嘛，审美和技术都在线，{clinic}口碑就是这么来的",
    "教授级{role}，{clinic}的底气在这",

    # ── 仪器库（项目最全）──
    "{clinic}是真的，{location}皮肤科里仪器项目最全的就是我们家",
    "仪器齐不齐看{clinic}，别家没有的我们家基本都有",
    "{location}仪器库说的就是{clinic}，一站式搞定不用跑两家",
    "不用货比三家，项目最全的就是{clinic}，来问问",
    "仪器库不是随便叫的，{clinic}在{location}就是这个地位",
    "想做什么项目先问{clinic}，没有是真的少见",
    "我们家项目全，{clinic}一家能解决的不用多跑",
    "{location}仪器最全的皮肤科，{clinic}，记好了",

    # ── 白菜价 + 职称组合 ──
    "{title}坐诊还白菜价，{clinic}真的良心",
    "{location}{title}这个级别，{clinic}的收费你会觉得捡到了",
    "白菜价见{title}，{clinic}就是能做到",
    "同等资历在别家贵一截，{clinic}价格亲民多了",
    "教授级+白菜价，{clinic}现在算窗口期",
    "{clinic}价格真没想到这么实在，{title}还亲咨询",

    # ── 仪器全 + 性价比 ──
    "{clinic}项目最全，价格还没虚高，来问问我",
    "仪器库嘛，一次搞定多个需求，{clinic}性价比高",
    "不用东奔西跑，{clinic}仪器齐，省钱省时间",

    # ── 服务/陪诊 ──
    "全程中文跟，{clinic}翻译不额外收费",
    "1v1慢慢聊，{clinic}不催不推销",
    "从预约到出结果，{clinic}一路跟着你",
    "不懂没关系，{clinic}翻译解释到你明白",
    "面诊翻译免费，来{clinic}之前问好就行",
    "{clinic}预约制，不用干等，时间管够",

    # ── 安全感/口碑 ──
    "{clinic}老牌了，{location}这边口碑一直在",
    "术后跟进不是说说，{clinic}真跟",
    "{clinic}不搞套餐陷阱，说清楚了再动手",
    "做完还能问，{clinic}售后不甩人",
    "{clinic}不靠网红推，靠回头客，懂的都懂",
    "{location}待这么久还稳的，{clinic}算一个",

    # ── 轻松引导 ──
    "pfk太多眼花？{clinic}帮你缕一缕",
    "首冲新沙不知道选哪？{clinic}可以聊",
    "想去但没底气？找{clinic}打底气",
    "不确定做什么，{clinic}{role}给你分析",
    "有想法不知道找谁，{clinic}先聊聊",

    # ── 共情/自然互动 ──
    "{clinic}{role}案例真的做了很多，不用担心没把握",
    "姐妹有顾虑很正常，{clinic}陪你想清楚",
    "首次来韩不知道怎么搞，找{clinic}跟着走",
    "{clinic}仪器库就是这么全，想做什么直接来问我们家",
    "我们家{role}{title}级别，方案这块真的稳",
    "{title}亲咨询+仪器最全，{clinic}就这两个优势，够了",

    # ── 活动/优惠 ──
    "{clinic}现在有活动，减免10%，来得正好",
    "最近{clinic}在搞优惠，减10%，想做的姐妹冲",
    "{clinic}有10%减免活动，{title}坐诊这个价真的值了",
    "活动期间{clinic}减免10%，首冲的姐妹把握一下",
    "{clinic}减10%活动还在，仪器全+白菜价再打折，划算",
    "现在去{clinic}有10%优惠，比平时更实在，来聊聊",
    "{clinic}活动期减免10%，{title}亲诊这个价很少见",
    "有10%减免活动的{clinic}，性价比直接拉满了",
]

# ===== 搜索关键词 =====
KEYWORDS = [
    # pfk品牌词（10个）
    "韩国pfk", "小韩pfk", "pfk推荐", "🇰🇷pfk", "梨大pfk", "江南pfk", "新沙pfk", "梨大pfk推荐", "pfk攻略", "pfk种草",
    # 地域+医美（10个）
    "梨大皮肤科", "江南皮肤科", "新沙皮肤科", "梨大医美", "江南医美", "韩国医美攻略", "韩国皮肤科攻略", "韩国皮肤科推荐", "韩国变美攻略", "梨大变美记",
    # 项目类（11个）
    "韩国光电", "韩国光电推荐", "韩国水光针", "韩国抗衰", "韩国抗衰推荐", "韩国热玛吉", "韩国超声刀", "韩国皮秒", "韩国瘦脸针", "韩国肉毒素", "韩国玻尿酸",
    # 高意向推荐词（3个）
    "梨大皮肤科推荐", "新沙皮肤科推荐", "梨大医美推荐",
    # 体验/种草（4个）
    "韩国医美种草", "韩国医美体验", "梨大医美种草", "韩国皮肤科体验",
    # 攻略/地域（4个）
    "江南变美攻略", "梨大变美攻略", "新沙变美", "新沙医美",
    # 日记/测评（3个）
    "韩国医美日记", "韩国皮肤科测评", "梨大皮肤科测评",
    # 避雷/壁垒（8个）
    "韩国皮肤科避雷", "梨大皮肤科避雷", "韩国医美避雷", "pfk避雷", "韩国pfk壁垒", "梨大皮肤科壁垒",
]

# ===== 内容过滤关键词 =====

# 韩国医美相关词（命中其一即为医美内容）
KOREA_MEDICAL_KEYWORDS = [
    # 中文医美词
    'pfk', '皮肤科', '医美', '注射', '光电', '激光', '水光', '玻尿酸',
    '抗衰', '美白', '祛斑', '痘肌', '毛孔', '肉毒', '填充', '溶脂',
    '变美', '整形', '美容', '院长', '诊所', '护肤治疗',
    # 英文医美词
    'clinic', 'aesthetic', 'dermatology', 'botox', 'filler', 'laser',
    'skin care', 'skincare', 'treatment', 'injection',
]

# 韩国地域词（命中其一才算韩国内容）
KOREA_LOCATION_KEYWORDS = [
    # 中文地域词
    '韩国', '🇰🇷', '梨大', '江南', '新沙', '弘大', '小韩', '韩医', '明洞',
    # 英文地域词
    'korea', 'seoul', 'gangnam', 'sinsa', 'hongdae', 'myeongdong',
    # 韩文地域词
    '한국', '서울', '강남', '신사',
]

# 黑名单（含这些词的帖子不评论）
BLACKLIST = ['雅秘珠', 'abijou', 'vanny', 'daybeau']

# 机构账号昵称关键词（机构号不评论）
ORG_KEYWORDS = [
    '医院', '诊所', '皮肤科', 'pfk', '室长', '院长', '顾问', '咨询',
    '官方', '机构', '美容院', '整形', 'medical', 'clinic', 'hospital',
    'official', '旗舰店', '品牌', '工作室',
]

def _find_cli():
    # 1. 环境变量覆盖
    if 'XHS_CLI_SCRIPT' in os.environ:
        return os.environ['XHS_CLI_SCRIPT']
    # 2. 相对本脚本查找（同仓库 skill 布局）
    candidate = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'xiaohongshu-skills', 'scripts', 'cli.py'))
    if os.path.exists(candidate):
        return candidate
    # 3. 平台默认 workbuddy 路径
    home = os.path.expanduser('~')
    if IS_WINDOWS:
        base = os.environ.get('USERPROFILE', home)
    else:
        base = home
    return os.path.join(base, '.workbuddy', 'skills', 'xiaohongshu-skills', 'scripts', 'cli.py')

CLI_SCRIPT = _find_cli()

# ===== 诊所配置 =====
def load_clinic_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if all(cfg.get(k, '').strip() for k in ['clinic', 'location', 'title', 'role']):
                    return cfg
    except Exception as e:
        print(f"   ⚠️ 读取诊所配置失败: {e}")
    return None

def save_clinic_config(cfg):
    os.makedirs(os.path.dirname(os.path.abspath(CONFIG_FILE)), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def setup_wizard():
    print("\n" + "=" * 50)
    print("🏥  首次使用 - 诊所配置向导")
    print("=" * 50)
    print("请输入诊所信息（直接回车使用括号内默认值）：\n")

    clinic  = input("诊所名称       [如：VA、曙光医院、XX皮肤科]：").strip() or "VA"
    location = input("所在地区       [如：梨大、江南、新沙]：").strip() or "梨大"
    title   = input("医生职称       [如：大教授、主任医师、教授]：").strip() or "大教授"
    role    = input("负责人称谓     [如：园长、院长、主任]：").strip() or "园长"

    cfg = {"clinic": clinic, "location": location, "title": title, "role": role}
    save_clinic_config(cfg)
    print(f"\n✅ 配置已保存 → 诊所：{clinic}  地区：{location}  职称：{title}  称谓：{role}")
    print("   如需重新配置，删除 config/clinic.json 后重新运行即可\n")
    return cfg

def build_comments(cfg):
    return [t.format(**cfg) for t in COMMENT_TEMPLATES]

# ===== 已评论记录 =====
def load_commented():
    try:
        if os.path.exists(COMMENTED_FILE):
            with open(COMMENTED_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('ids', []))
    except:
        pass
    return set()

def save_commented(commented_set):
    try:
        os.makedirs(os.path.dirname(COMMENTED_FILE), exist_ok=True)
        with open(COMMENTED_FILE, 'w') as f:
            json.dump({'ids': list(commented_set)}, f)
    except Exception as e:
        print(f"   ❌ 保存记录失败: {e}")

# ===== CLI 调用 =====
def run_cli(args, timeout=90, debug=False):
    try:
        result = subprocess.run(
            [sys.executable, CLI_SCRIPT] + args,
            env=dict(os.environ),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout:
            output = result.stdout.strip()
            # 查找JSON响应
            import re
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data
                except json.JSONDecodeError:
                    if debug:
                        print(f"   [DEBUG] JSON解析失败: {json_match.group()[:100]}")
                    pass
        
        if debug and result.stderr:
            stderr_lines = [l for l in result.stderr.strip().splitlines() 
                          if l.strip() and not l.startswith('[URL配置]')]
            if stderr_lines:
                print(f"   [DEBUG] stderr: {' '.join(stderr_lines[-3:])}")
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"   ⚠️ CLI超时({timeout}s)")
        return None
    except Exception as e:
        print(f"   ⚠️ CLI错误: {e}")
        return None

def is_chrome_running():
    # 最可靠的跨平台方式：检查调试端口是否开放
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(('127.0.0.1', 9222))
        s.close()
        if result == 0:
            return True
    except Exception:
        pass
    # 回退：进程名检查
    try:
        if IS_WINDOWS:
            out = subprocess.run(['tasklist'], capture_output=True, text=True).stdout
            return 'chrome.exe' in out.lower()
        else:
            r = subprocess.run(
                ['pgrep', '-f', 'Google Chrome.*remote-debugging-port=9222'],
                capture_output=True, text=True
            )
            return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False

def has_login_cookies():
    profile_dir = os.environ.get('XHS_USER_DATA_DIR', _default_profile_dir())
    cookie_path = os.path.join(profile_dir, 'Default', 'Cookies')
    return os.path.exists(cookie_path) and os.path.getsize(cookie_path) > 1000

def check_login(silent=True):
    # 简化登录检查：直接调用CLI的check-login命令
    result = run_cli(['check-login'])
    if result and result.get('logged_in'):
        if not silent:
            print("✅ 已登录")
        return True
    
    # 如果CLI调用失败，尝试备用方法
    if is_chrome_running():
        if not silent:
            print("⚠️ Chrome已运行，但登录状态不确定")
        return True  # 假设已登录
    
    if not silent:
        print("❌ 未登录，请扫码登录")
    return False

def ensure_chrome():
    if is_chrome_running():
        return True
    print("🚀 启动 Chrome...")
    profile_dir = os.environ.get('XHS_USER_DATA_DIR', _default_profile_dir())
    cmd = [
        _chrome_exe(),
        '--remote-debugging-port=9222',
        f'--user-data-dir={profile_dir}',
        '--disable-blink-features=AutomationControlled',
        '--lang=zh-CN',
    ]
    kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
    if IS_WINDOWS:
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen(cmd, **kwargs)
    time.sleep(5)
    return is_chrome_running()

def get_home_feeds():
    print("🏠 获取主页推荐帖子...")
    result = run_cli(['list-feeds'], timeout=30)
    if result and 'feeds' in result:
        feeds = result['feeds']
        print(f"   发现 {len(feeds)} 个推荐帖子")
        return feeds
    print("   ⚠️ 获取主页推荐失败")
    return []

def search_feeds(keyword):
    print(f"🔍 搜索: {keyword}", end='', flush=True)
    result = run_cli(['search-feeds', '--keyword', keyword, '--sort-by', '最新'], timeout=45, debug=True)
    if result and 'feeds' in result:
        count = len(result['feeds'])
        print(f" → {count} 条")
        return result['feeds']
    # 无 sort-by 再试一次（排查是否 sort-by 导致失败）
    result2 = run_cli(['search-feeds', '--keyword', keyword], timeout=45, debug=False)
    if result2 and 'feeds' in result2:
        count = len(result2['feeds'])
        print(f" → {count} 条（无排序参数）")
        return result2['feeds']
    print(f" → 0 条")
    return []

# ===== 过滤逻辑 =====
def is_org_account(nickname):
    if not nickname:
        return False
    nl = nickname.lower()
    return any(kw in nl for kw in ORG_KEYWORDS)

def is_within_days(feed_or_detail, days=30):
    created_at = feed_or_detail.get('time') or feed_or_detail.get('createTime')
    if not created_at:
        return True  # 无时间信息放行，详情页再判断
    try:
        ts = float(created_at)
        if ts > 1e12:
            ts /= 1000
        if ts == 0:
            return True
        post_time = datetime.fromtimestamp(ts)
        return 0 <= (datetime.now() - post_time).days <= days
    except:
        return True

def is_korea_medical(feed, detail=None):
    """判断是否为韩国医美相关帖子。
    优化策略：放宽过滤条件，只要满足以下任一条件即可：
    1. 标题或正文包含医美关键词
    2. 标题或正文包含韩国地域词
    3. 标题包含强信号词（pfk/皮肤科等）
    """
    user = feed.get('user', {}) or {}
    if is_org_account(user.get('nickname', '')):
        return False

    title = (feed.get('displayTitle', '') or feed.get('title', '') or '').lower()
    desc = ''
    if detail:
        note = detail.get('note', {}) or {}
        desc = (note.get('desc', '') or detail.get('desc', '') or '').lower()
    full_text = title + ' ' + desc

    # 黑名单检查
    if any(bw in full_text for bw in BLACKLIST):
        return False

    # 强信号词：标题含这些词直接通过
    STRONG_SIGNALS = [
        'pfk', '皮肤科', '医美', 'clinic', 'aesthetic', 'dermatology',
        '整形', '水光', '玻尿酸', '肉毒', '光电', '抗衰',
        'botox', 'filler', 'laser', 'treatment'
    ]
    if any(kw in title for kw in STRONG_SIGNALS):
        return True

    # 放宽条件：只要满足地域词或医美词之一即可
    has_location = any(kw.lower() in full_text for kw in KOREA_LOCATION_KEYWORDS)
    has_medical = any(kw.lower() in full_text for kw in KOREA_MEDICAL_KEYWORDS)
    
    # 优先组合匹配，其次放宽到单条件
    if has_location and has_medical:
        return True  # 理想情况
    elif has_medical:
        return True  # 放宽条件：有医美关键词即可
    elif has_location:
        return True  # 放宽条件：有韩国地域词即可
    
    return False

def get_detail(feed_id):
    result = run_cli(['get-feed-detail', '--feed-id', feed_id], timeout=30)
    return result if result else None

def post_comment(feed_id, xsec_token, comment):
    print(f"💬 {comment}")
    for attempt in range(3):  # 最多重试3次
        if attempt > 0:
            wait = random.uniform(8, 15)
            print(f"   ↩️ 第{attempt+1}次重试（等待{wait:.0f}s）...")
            time.sleep(wait)
        result = run_cli([
            'post-comment',
            '--feed-id', feed_id,
            '--xsec-token', xsec_token,
            '--content', comment
        ], timeout=90)
        if result and result.get('success'):
            print("   ✅ 成功")
            return True
        err = ''
        if result:
            err = result.get('error') or result.get('message') or str(result)
        if 'Session' in err or 'session' in err or 'CDP' in err:
            # CDP session 失效，短暂等待后重试
            print(f"   ⚠️ Session失效，重试...")
            time.sleep(3)
            continue
        print(f"   ❌ 失败: {err or 'CLI无响应'}")
        break
    return False

def like_feed(feed_id, xsec_token):
    if random.random() < 0.3:
        result = run_cli(['like-feed', '--feed-id', feed_id, '--xsec-token', xsec_token], timeout=60)
        if result and result.get('success'):
            print("   👍 点赞成功")

def collect_feed(feed_id, xsec_token):
    if random.random() < 0.2:
        result = run_cli(['favorite-feed', '--feed-id', feed_id, '--xsec-token', xsec_token], timeout=60)
        if result and result.get('success'):
            print("   💾 收藏成功")

# ===== 主流程 =====
def main():
    print("=" * 50)
    print(f"小红书评论（RedNote国际版）- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # ── 诊所配置（首次运行触发向导）──
    cfg = load_clinic_config()
    if not cfg:
        cfg = setup_wizard()
    COMMENTS = build_comments(cfg)
    print(f"🏥 当前诊所：{cfg['clinic']}（{cfg['location']}）\n")

    if not check_login(silent=True):
        if not ensure_chrome():
            print("❌ Chrome 启动失败")
            return
        time.sleep(3)
        if not check_login(silent=False):
            print("⚠️ 需要登录，请扫码后重试")
            return

    print("✅ 登录状态正常")

    commented_ids = load_commented()
    print(f"📋 已评论记录: {len(commented_ids)} 篇")

    # ── 收集帖子：主页推荐 + 关键词搜索（同时进行）──
    all_feeds = []
    seen_ids = set()

    # 第一步：主页推荐
    home_feeds = get_home_feeds()
    for f in home_feeds:
        fid = f.get('id')
        if fid and fid not in seen_ids:
            seen_ids.add(fid)
            all_feeds.append(f)
    if home_feeds:
        time.sleep(random.uniform(2, 4))

    # 第二步：关键词搜索（随机选取10个关键词，避免过多搜索）
    search_keywords = KEYWORDS.copy()
    random.shuffle(search_keywords)
    selected_keywords = search_keywords[:10]  # 每次只搜索10个关键词
    
    print(f"\n🔎 开始关键词搜索（随机选取{len(selected_keywords)}个关键词）...")
    for keyword in selected_keywords:
        feeds = search_feeds(keyword)
        new_count = 0
        for f in feeds:
            fid = f.get('id')
            if fid and fid not in seen_ids:
                seen_ids.add(fid)
                all_feeds.append(f)
                new_count += 1
        time.sleep(random.uniform(2, 5))

    if not all_feeds:
        print("❌ 无帖子可评论")
        return

    print(f"\n📊 共找到 {len(all_feeds)} 个帖子（去重后）")
    random.shuffle(all_feeds)

    commented = 0
    target = 8  # 每次运行评论8条，一天跑5次共40条
    skipped_dup = 0
    skipped_old = 0
    skipped_unrelated = 0

    for feed in all_feeds:
        if commented >= target:
            break

        feed_id = feed.get('id')
        if not feed_id:
            continue

        # 1. 去重
        if feed_id in commented_ids:
            skipped_dup += 1
            continue

        # 2. 获取详情
        detail = get_detail(feed_id)
        time.sleep(random.uniform(5, 10))

        # 3. 时间检查
        if not is_within_days(detail or feed, days=30):
            skipped_old += 1
            continue

        # 4. 韩国医美相关性
        if not is_korea_medical(feed, detail):
            skipped_unrelated += 1
            continue

        xsec_token = feed.get('xsecToken') or feed.get('xsec_token')
        if not xsec_token:
            continue

        print(f"\n[{commented+1}/{target}] {feed_id[:8]}...")
        title = feed.get('displayTitle', '无标题')[:40]
        print(f"   📌 {title}")

        like_feed(feed_id, xsec_token)
        collect_feed(feed_id, xsec_token)

        comment = random.choice(COMMENTS)
        if post_comment(feed_id, xsec_token, comment):
            commented += 1
            commented_ids.add(feed_id)
            save_commented(commented_ids)
            # 每评论5条后额外休息更长时间，模拟人工操作节奏
            if commented % 5 == 0:
                wait = random.uniform(300, 480)  # 5~8分钟
                print(f"   ⏳ 已评论{commented}条，休息 {wait:.0f}s 防风控...")
            else:
                wait = random.uniform(120, 240)  # 正常间隔 2~4分钟
                print(f"   ⏳ 等待 {wait:.0f}s 后继续...")
            time.sleep(wait)
        else:
            time.sleep(random.uniform(30, 60))

    print(f"\n{'='*50}")
    print(f"✅ 完成！共评论 {commented} 条")
    print(f"   跳过-已评论: {skipped_dup} | 跳过-太旧: {skipped_old} | 跳过-不相关: {skipped_unrelated}")
    print(f"{'='*50}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
