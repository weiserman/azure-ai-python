#!/bin/bash
PROTOCOL=https
HOST=main-pnp-linux-function-app.azurewebsites.net
PORT=443
curl -v -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -F "header=Test Header" \
  -F "subject=Test Subject" \
  -F "recipient=test@example.com" \
  -F "body=This is a test email body." \
  -F "attachments=@/mnt/c/tmp/b.png"
