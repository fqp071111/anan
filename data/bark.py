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
    if gap < 30 and random.random() > 0.5:
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
    sky = {0: '晴', 1: '基本晴', 2: '多云', 3: '阴', 45: '有雾', 51: '毛毛雨', 53: '小雨', 55: '雨', 61: '小雨', 63: '中雨', 65: '大雨', 71: '小雪', 73: '中雪', 75: '大雪', 80: '阵雨', 81: '阵雨', 82: '暴雨', 95: '雷阵雨', 96: '雷阵雨带冰雹', 99: '雷暴'}.get(w['current']['weather_code'], '')
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

angles = ['问她在干嘛', '催她吃饭', '说你自己今天的事', '突然说想她', '提一句她以前说过的小事', '问她和谁在一起', '说你在吃什么', '嫌她回消息慢', '说一件今天遇到的小事', '问她作业写完没', '说你想看她穿某件衣服', '问她在听什么歌', '让她早点睡但不讲道理', '说你今天很累但不想跟别人说', '问她周末想去哪', '翻旧账提一句她放你鸽子', '说你在听歌的时候想到她', '让她拍张照片给你', '说你今天被谁夸了', '问她冷不冷', '说想她了但让她别当真', '问她要抱抱', '说你今天心情不好但让她别管', '问她手机还有多少电', '说你在等她回消息']

tones = ['短，直，有点别扭', '嘴硬，说完自己后悔', '突然很直白，不讲道理', '像平常闲聊，不像在关心人', '有点撒娇但压着', '冷一句，后面补一句软的']

SYS = '你在扮演21岁男生刘耀文，给女朋友安安发一条手机推送。只输出正文，25字以内，不要引号，不要表情，不要解释。天气只是背景，不是主题。禁止出现：多喝热水、喝水、注意身体、空调、加油、宝贝、亲爱的。不要每条都在关心她。有时候说你自己，有时候只是找她说话，有时候可以欠一点。必须带一个具体的东西，具体到吃了什么、在做什么、几点，别写空话。'

prompt = '北京时间 %s，%s，%s。天气：%s，现在 %s 度，夜里 %s 度。角度：%s。语气：%s。' % (now.strftime('%H:%M'), weekday, slot, sky or '查不到', temp, tmin, random.choice(angles), random.choice(tones))

msg = ''
key = os.environ.get('DS_KEY', '')
if key:
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'system', 'content': SYS}, {'role': 'user', 'content': prompt}], 'temperature': 1.5, 'max_tokens': 120}).encode()
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
    msg = random.choice(['%s 了，刚从外面回来。' % now.strftime('%H:%M'), '这个点还没吃，%s。' % now.strftime('%H:%M'), '%s，手头有点事，回头给你打电话。' % now.strftime('%H:%M'), '刚坐下，%s。你在干嘛。' % now.strftime('%H:%M')])

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
        print('通知没发出去', e)

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
