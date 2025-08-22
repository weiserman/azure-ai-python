#!/bin/bash
PROTOCOL=http
HOST=localhost
PORT=7071
curl -s -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -F "header=Test Header" \
  -F "subject=Test Subject" \
  -F "recipient=test@example.com" \
  -F "body=This is a test email body." \
  -F "attachments=@./res/a.png"
rm -f "$TMP1" "$TMP2"
