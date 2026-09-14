import json, os
from pywebpush import webpush
M='data/pushed.txt'
s=json.load(open('data/subscription.json'))
m=(os.environ.get('MSG') or '').strip()
u=(os.environ.get('NURL') or './phone/index.html').strip()
k='d|'+m
if not m:
    try:
        c=json.load(open('data/chat.json'))
    except Exception:
        c=[]
    a=[x for x in c if x.get('from')=='me' and x.get('text')]
    if a:
        m=a[-1]['text']
        k='c|'+str(a[-1].get('time',''))+'|'+m
o=open(M).read().strip() if os.path.exists(M) else ''
if not m or k==o:
    raise SystemExit
webpush(subscription_info=s, data=json.dumps({'title':'刘耀文','body':m,'url':u}), vapid_private_key='data/vapid_private.pem', vapid_claims={'sub':'mailto:anan@example.com'})
open(M,'w').write(k)
os.system('git add data/pushed.txt; git commit -q -m mark || true; git push -q || true')
