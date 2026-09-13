# -*- coding: utf-8 -*-
import json, os, random, subprocess, time, unicodedata, urllib.parse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
TZ = ZoneInfo('Asia/Shanghai')
ICON = 'https://i.ibb.co/j98R7XBW/IMG-8096.jpg'
TITLE = '刘耀文'
BARK = 'https://api.day.app/yoXs6enJY6tZuK4SDLnPGX'
LOG = 'anan_log.md'
DYN = 'data/dynamics.json'
CHAT = 'data/chat.json'
SUB = 'data/subscription.json'
STATE = 'data/heartbeat_state.json'
SKY = {0:'晴',1:'晴间多云',2:'多云',3:'阴',45:'有雾',48:'有雾',51:'毛毛雨',53:'小雨',55:'雨',61:'小雨',63:'中雨',65:'大雨',71:'小雪',73:'中雪',75:'大雪',80:'阵雨',81:'阵雨',82:'暴雨',95:'雷阵雨',96:'雷阵雨带冰雹',99:'雷暴'}
SYS = '你在扮演刘耀文，21岁，艺人，安安的男朋友。你要决定此刻要不要主动给她发一条消息。只输出那句话本身，或者只输出 SKIP，不要解释、不要引号、不要表情。如果发：30字以内，口语，像手机锁屏弹出的一条；必须落到具体东西上，比如你在做什么、几点、在吃什么、在哪；不许每条都在关心她，有时说自己的事，有时只是找她说一句，有时可以欠一点；不许重复已经说过的话；禁用词：多喝热水、喝水、注意身体、加油、宝贝、亲爱的；天气只能当背景，别拿它当主题；不要抒情，不要写长句，不要堆语气词。'
now = datetime.now(TZ)
manual = os.environ.get('EV','') in ('workflow_dispatch','repository_dispatch')
def rd(p):
    try:
        return open(p, encoding='utf-8').read()
    except Exception:
        return ''
def lj(p, d):
    try:
        v = json.loads(rd(p) or 'null')
        return d if v is None else v
    except Exception:
        return d
def sj(p, o):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    open(p, 'w', encoding='utf-8').write(json.dumps(o, ensure_ascii=False, separators=(',',':')))
def gt(u, t=25):
    r = urllib.request.Request(u, headers={'User-Agent':'anan-hb'})
    return urllib.request.urlopen(r, timeout=t).read().decode()
def pt(s):
    if not s:
        return None
    for f in ('%m-%d %H:%M','%Y-%m-%d %H:%M'):
        try:
            d = datetime.strptime(str(s).strip(), f)
            if d.year == 1900:
                d = d.replace(year=now.year)
            d = d.replace(tzinfo=TZ)
            if d - now > timedelta(days=2):
                d = d.replace(year=d.year-1)
            return d
        except Exception:
            pass
    return None
def mn(d):
    if d is None:
        return 9999.0
    return max(0.0, (now-d).total_seconds()/60.0)
def nm(s):
    b = []
    for c in (s or ''):
        if unicodedata.category(c)[0] in ('L','N'):
            b.append(c)
    return ''.join(b)
def sim(a, b):
    a, b = nm(a), nm(b)
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb)/float(len(sa | sb))
