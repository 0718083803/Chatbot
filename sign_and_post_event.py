import hmac,hashlib,time,json,urllib.request,ssl
secret='2e50228d2c19fc4f4156aa9f27e6a25b'
ts=str(int(time.time()))
payload={
  "type":"event_callback",
  "event":{
    "type":"message",
    "channel":"C1234567890",
    "text":"What time is lunch?"
  }
}
body=json.dumps(payload).encode('utf-8')
basestring=f"v0:{ts}:{body.decode('utf-8')}"
sig='v0='+hmac.new(secret.encode(),basestring.encode('utf-8'),hashlib.sha256).hexdigest()
req=urllib.request.Request('https://nuclear-rebuilt-staunch.ngrok-free.dev/slack/events', data=body, headers={'Content-Type':'application/json','X-Slack-Request-Timestamp':ts,'X-Slack-Signature':sig})
ctx=ssl.create_default_context()
ctx.check_hostname=False
ctx.verify_mode=ssl.CERT_NONE
with urllib.request.urlopen(req, context=ctx) as res:
    print(res.status)
    print(res.read().decode())
