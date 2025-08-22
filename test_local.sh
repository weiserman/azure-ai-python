#!/bin/bash
PROTOCOL=http
HOST=localhost
PORT=7071
<<COMMENT_BLOCK
COMMENT_BLOCK
curl -v -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -H "Content-Type: application/json; charset=utf8" \
  -d '{
    "header": "Test Header",
    "subject": "Test Subject",
    "recipient": "test@example.com",
    "attachments":[
    	"'$(convert rose: --format png - |base64 -w0)'",
    	"'$(convert rose: --format png - |base64 -w0)'"
    ],
    "body": "This is a test email body."
  }' | jq '.'
curl -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
    -F "header=Test Header" \
    -F "subject=Test Subject" \
    -F "recipient=test@example.com" \
    -F "body=This is a test email body." \
    -F "attachments=@./a.png" \
    -F "attachments=@./b.png" \
    -F "attachments=@./c.png" | jq '.'
