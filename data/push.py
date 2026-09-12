import json
from pywebpush import webpush

sub = json.load(open('data/subscription.json'))
d = json.load(open('data/dynamics.json'))
last = d[-1]

webpush(
    subscription_info=sub,
    data=json.dumps({'title': '小狗日记', 'body': last['text'], 'url': './index.html'}),
    vapid_private_key='data/vapid_private.pem',
    vapid_claims={'sub': 'mailto:anan@example.com'}
)
