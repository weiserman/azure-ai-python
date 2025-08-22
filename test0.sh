#!/bin/bash
PROTOCOL=http
HOST=localhost
PORT=7071
BODY=$(mktemp /tmp/payload.XXXXXX.json)
echo '{
	"header":"Test Header",
	"subject":"Test Subject",
	"recipient":"test@example.com",
	"attachments":[
		"'$(cat ./res/a.png|base64 -w0)'"
	],
	"body":"This is a test email body."
}'>$BODY
curl -s -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -H "Content-Type: application/json; charset=utf8" \
  --data "@$BODY"
