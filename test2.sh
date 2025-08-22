#!/bin/bash
PROTOCOL=https
HOST=main-pnp-linux-function-app.azurewebsites.net
PORT=443
BODY=$(mktemp /tmp/payload.XXXXXX.json)
echo '{
	"header":"Test Header",
	"subject":"Test Subject",
	"recipient":"test@example.com",
	"attachments":[
		"'$(cat /mnt/c/tmp/b.png|base64 -w0)'"
	],
	"body":"This is a test email body."
}'>$BODY
curl -s -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -H "Content-Type: application/json; charset=utf8" \
  --data "@$BODY"
rm $BODY
