import json
from pywebpush import webpush
sub=json.load(open('data/subscription.json'))
d=json.load(open('data/chat.json'))
mine=[m for m in d if m.get('from')=='me']
last=mine[-1] if mine else {'text':'我在'}
webpush(
 subscription_info=sub,
 data=json.dumps({'title':'刘耀文','body':last['text'],'url':'./phone/index.html'}),
 vapid_private_key='data/vapid_private.pem',
 vapid_claims={'sub':'mailto:anan@example.com'}
)
