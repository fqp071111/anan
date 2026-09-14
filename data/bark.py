import os, json, time, random, subprocess, urllib.parse, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ICON = 'https://i.ibb.co/j98R7XBW/IMG-8096.jpg'
TITLE = '刘耀文'
BARK = 'https://api.day.app/yoXs6enJY6tZuK4SDLnPGX'
LOG = 'anan_log.md'
DYN = 'data/dynamics.json'
SUB = 'data/subscription.json'

now = datetime.now(ZoneInfo('Asia/Shanghai'))
hour = now.hour
manual = os.environ.get('EV', '') in ('workflow_dispatch', 'repository_dispatch')

last = None
try:
    rows = [x for x in open(LOG, encoding='utf-8').read().splitlines() if x.strip()]
    if rows:
        last = datetime.strptime('2026-' + rows[-1][2:13], '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Shanghai'))
except Exception:
    last = None

gap = 999.0 if last is None else (now - last).total_seconds() / 60.0

if not manual:
    if hour >= 2 and hour < 7:
        raise SystemExit
    if gap < 240 and random.random() > 0.25:
        raise SystemExit
    time.sleep(random.randint(0, 30))

def get(url, timeout=20):
    return urllib.request.urlopen(url, timeout=timeout).read().decode()

temp = tmin = None
sky = ''
try:
    w = json.loads(get('https://api.open-meteo.com/v1/forecast?latitude=39.9042&longitude=116.4074&current=temperature_2m,weather_code&daily=temperature_2m_min&timezone=Asia%2FShanghai'))
    temp = w['current']['temperature_2m']
    tmin = w['daily']['temperature_2m_min'][0]
    sky = {0: '晴', 1: '基本晴', 2: '多云', 3: '阴', 45: '雾霾', 51: '毛毛雨', 61: '小雨', 63: '中雨', 65: '大雨', 80: '阵雨', 95: '雷阵雨'}.get(w['current']['weather_code'], '')
except Exception:
    pass

weekday = '周' + '一二三四五六日'[now.weekday()]
if hour >= 23 or hour < 2:
    slot = '深夜'
elif hour < 9:
    slot = '早上'
elif hour < 12:
    slot = '上午'
elif hour < 14:
    slot = '中午'
elif hour < 18:
    slot = '下午'
elif hour < 22:
    slot = '晚上'
else:
    slot = '深夜'

angles = ['今天练舞时的一个细节', '球场上的一件小事', '家里打来的电话', '翻出来的一件旧东西', '嘴硬之后自己跟自己算账', '看见消息时的心情', '被人夸完之后的空', '跟人较劲的一点小事', '排练里出的一个小错', '躺着还没睡着的念头', '路过某个地方的联想', '往后的打算', '把话咽回去之后的后悔', '天冷了不情愿地想起谁']

tones = ['平静，像在跟自己讲一件已经过去的事', '别扭，承认一半又收回去', '突然很直白，不修饰', '有点自嘲', '只记一件事，不抒情', '像随口一说，其实挺在意']

SYS = '你在写只给自己看的日记，写的人是21岁的男艺人刘耀文。只写内心：今天做了什么、心里冒出来的念头、别扭和自我较劲，可以提到女朋友，但用她，不许对她说话，不许提问，不许要她回话。只输出正文，40字以内，不要引号，不要表情，不要写时间，不要解释。禁止出现：多喝热水、注意身体、早点睡、加油、宝贝、亲爱的。不许写梦，不许写风、蝉、海、月光、裙子这类虚的意象，不许编造没发生的行程。像真人随手记下的一句，前后要有因果，不要总是吃吃喝喝，不许重复最近写过的内容。'

recent = []
try:
    _d = json.load(open(DYN, encoding='utf-8'))
    if isinstance(_d, list):
        recent = [x.get('text', '') for x in _d[-8:] if isinstance(x, dict) and x.get('text')]
except Exception:
    recent = []

prompt = '北京时间 %s，%s，%s。天气：%s，现在 %s 度，夜间 %s 度。写一件今天真实发生的小事，或者一个冒出来的念头，方向参考：%s。语气：%s。不要拿时间或天气开头，天气只是背景。' % (now.strftime('%H:%M'), weekday, slot, sky or '查不到', temp, tmin, random.choice(angles), random.choice(tones))
if recent:
    prompt += '最近写过这些，不许重复，也不许换个说法说同一件事：%s。' % ' / '.join(recent)

msg = ''
key = os.environ.get('DS_KEY', '')
if key:
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'system', 'content': SYS}, {'role': 'user', 'content': prompt}], 'temperature': 0.9, 'max_tokens': 80}).encode()
    for i in range(2):
        try:
            req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
            msg = json.loads(urllib.request.urlopen(req, timeout=45).read().decode())['choices'][0]['message']['content'].strip()
            if msg:
                break
        except Exception as e:
            print('模型没回话', e)
            time.sleep(3)

if not msg:
    msg = random.choice(['今天练得有点过，腿到现在还是酸的。', '球馆的灯坏了一盏，投不准也怪不了谁。', '手机翻了几遍，最后还是什么都没发出去。', '有段舞还没排顺，闭上眼还在数拍子。'])

try:
    d = json.load(open(DYN, encoding='utf-8'))
    if not isinstance(d, list):
        d = []
except Exception:
    d = []
d.append({'kind': 'dynamic', 'text': msg, 'time': now.strftime('%m-%d %H:%M')})
d = d[-200:]
with open(DYN, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, separators=(',', ':'))

os.environ['MSG'] = msg
os.environ['NURL'] = './index.html'

ok = True
if os.path.exists(SUB) and os.path.getsize(SUB) > 2:
    try:
        subprocess.run(['pip', 'install', '-q', 'pywebpush'], check=False)
        ok = subprocess.run(['python3', 'data/push.py'], check=False).returncode == 0
    except Exception as e:
        ok = False
        print('通知没发出', e)

if not ok:
    try:
        get('%s/%s/%s?icon=%s' % (BARK, urllib.parse.quote(TITLE), urllib.parse.quote(msg, safe=''), ICON))
    except Exception as e:
        print('兜底也没发出去', e)

print(msg)

rows = [x for x in open(LOG, encoding='utf-8').read().splitlines() if x.strip()]
rows.append('- %s | %s' % (now.strftime('%m-%d %H:%M'), msg))
if len(rows) > 300:
    rows = rows[-300:]
open(LOG, 'w', encoding='utf-8').write(chr(10).join(rows) + chr(10))
