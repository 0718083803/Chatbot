$t=(Get-Content .env | Where-Object {$_ -match '^SLACK_BOT_TOKEN='}) -replace '^SLACK_BOT_TOKEN=',''
$res = Invoke-RestMethod -Uri 'https://slack.com/api/auth.test' -Headers @{Authorization="Bearer $t"} -Method Post
$res | ConvertTo-Json -Depth 5
