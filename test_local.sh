#!/bin/bash
PROTOCOL=http
HOST=localhost
PORT=7071
# Generate temp files for the images
TMP1=$(mktemp /tmp/attach1.XXXXXX.png)
TMP2=$(mktemp /tmp/attach2.XXXXXX.png)
convert rose: -resize 1x1 "$TMP1"
convert rose: -resize 1x1 "$TMP2"
<<COMMENT_BLOCK
COMMENT_BLOCK
curl -v -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -H "Content-Type: application/json; charset=utf8" \
  -d '{
    "header": "Test Header",
    "subject": "Test Subject",
    "recipient": "test@example.com",
    "attachments":[
    	"'$(convert rose: -resize 1x1 --format png - |base64 -w0)'",
    	"'$(convert rose: -resize 1x1 --format png - |base64 -w0)'"
    ],
    "body": "This is a test email body."
  }' | jq '.'
curl -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -F "header=Test Header" \
  -F "subject=Test Subject" \
  -F "recipient=test@example.com" \
  -F "body=This is a test email body." \
  -F "attachments=@$TMP1" \
  -F "attachments=@$TMP2" | jq '.'
rm -f "$TMP1" "$TMP2"
