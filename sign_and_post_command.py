import hmac,hashlib,time,ssl,urllib.request,urllib.parse
secret='2e50228d2c19fc4f4156aa9f27e6a25b'
params={'token':'ignored','team_id':'T0266FRGM','team_domain':'hackclub','channel_id':'C1234567890','channel_name':'random','user_id':'U123','user_name':'tester','command':'/bot-ping','text':'','response_url':'https://example.com/response'}
body=urllib.parse.urlencode(params).encode('utf-8')
ts=str(int(time.time()))
basestring=f"v0:{ts}:{body.decode('utf-8')}"
sig='v0='+hmac.new(secret.encode(),basestring.encode('utf-8'),hashlib.sha256).hexdigest()
req=urllib.request.Request('https://nuclear-rebuilt-staunch.ngrok-free.dev/slack/commands', data=body, headers={'Content-Type':'application/x-www-form-urlencoded','X-Slack-Request-Timestamp':ts,'X-Slack-Signature':sig})
ctx=ssl.create_default_context()
ctx.check_hostname=False
ctx.verify_mode=ssl.CERT_NONE
with urllib.request.urlopen(req, context=ctx) as res:
    print(res.status)
    print(res.read().decode())
