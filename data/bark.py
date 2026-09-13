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
    if hour < 7 or hour >= 23:
        raise SystemExit
    if gap < 25 and random.random() > 0.5:
        raise SystemExit
    time.sleep(random.randint(0, 40))

def get(url, timeout=20):
    return urllib.request.urlopen(url, timeout=timeout).read().decode()

temp = tmin = None
sky = ''
try:
    w = json.loads(get('https://api.open-meteo.com/v1/forecast?latitude=39.9042&longitude=116.4074&current=temperature_2m,weather_code&daily=temperature_2m_min&timezone=Asia%2FShanghai'))
    temp = w['current']['temperature_2m']
    tmin = w['daily']['temperature_2m_min'][0]
    sky = {0: '晴', 1: '基本晴', 2: '多云', 3: '阴', 45: '雾霾', 51: '毛毛雨', 53: '小雨', 55: '雨', 61: '小雨', 63: '中雨', 65: '大雨', 71: '小雪', 73: '中雪', 75: '大雪', 80: '阵雨', 81: '阵雨', 82: '暴雨', 95: '雷阵雨', 96: '雷阵雨伴冰雹', 99: '雷暴'}.get(w['current']['weather_code'], '')
except Exception:
    pass

weekday = '周' + '一二三四五六日'[now.weekday()]
if hour < 9:
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

angles = ['问她在干嘛', '问她吃饭没', '问她作业写完没', '问她冷不冷', '问她在听什么歌', '问她周末想去哪', '问她今天过得怎么样', '问她困不困', '说你现在有点想她', '说你刚忙完', '说你在等她的消息', '说天冷让她穿厚一点', '说想看她拍张照片给你', '让她别熬太晚', '问她要不要打电话', '问她跟谁在一起', '说她回消息太快你有点不适应', '说你想抱她一下']

tones = ['简短，直，有点别扭', '别扭，说完自己后悔', '突然很直白，不讲道理', '像平常聊天，不像在哄人', '有点挑刺但压着', '冷一句，后面补一句软的']

SYS = '你在扮演21岁男艺人刘耀文，给女朋友安安发一条手机推送。只输出正文，30字以内，不要引号，不要表情，不要解释。天气只是背景，不是主题。禁止出现：多喝热水、喝水、注意身体、早点睡、加油、宝贝、亲爱的。不要每句都在关心她，有时候只是找她说话，有时候可以夸一点。必须带一个具体的东西：她可能吃了什么、在做什么、现在几点。最重要的一条：只准用题面给的事实，不准写梦，不准写风、蝉、海、月光、裙子这类虚的意象，不准编自己今天去了哪见了谁，像真人随手发微信一样说大白话。'

recent = []
try:
    _d = json.load(open(DYN, encoding='utf-8'))
    if isinstance(_d, list):
        recent = [x.get('text', '') for x in _d[-8:] if isinstance(x, dict) and x.get('text')]
except Exception:
    recent = []

prompt = '北京时间 %s，%s，%s。天气：%s，现在 %s 度，夜间 %s 度。想聊的方向：%s。语气：%s。' % (now.strftime('%H:%M'), weekday, slot, sky or '查不到', temp, tmin, random.choice(angles), random.choice(tones))
if recent:
    prompt += '你最近已经发过这些，不许重复，也不许换个说法说同一件事：%s。' % ' / '.join(recent)

msg = ''
key = os.environ.get('DS_KEY', '')
if key:
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'system', 'content': SYS}, {'role': 'user', 'content': prompt}], 'temperature': 0.85, 'max_tokens': 80}).encode()
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
    msg = random.choice(['%s 了，刚从外面回来。' % now.strftime('%H:%M'), '这个点还没吃，%s。' % now.strftime('%H:%M'), '%s，手头有点事，回头打给你。' % now.strftime('%H:%M'), '刚坐下，%s。你在干嘛。' % now.strftime('%H:%M')])

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

rows = open(LOG, encoding='utf-8').read().splitlines()
rows.append('- %s | %s' % (now.strftime('%m-%d %H:%M'), msg))
if len(rows) > 300:
    rows = rows[-300:]
open(LOG, 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
