#!/bin/bash
PROTOCOL=http
HOST=localhost
PORT=7071
#curl "$PROTOCOL://$HOST:$PORT/api/HelloWorldFunction?name=YourName" 
#curl "$PROTOCOL://$HOST:$PORT/api/foo"
#curl "$PROTOCOL://$HOST:$PORT/api/bar"
#curl "$PROTOCOL://$HOST:$PORT/api/baz"
#curl "$PROTOCOL://$HOST:$PORT/api/callws?wsurl=https://example.com"
curl -X POST "$PROTOCOL://$HOST:$PORT/api/callai" \
  -H "Content-Type: application/json" \
  -d '{
    "header": "Test Header",
    "subject": "Test Subject",
    "recipient": "test@example.com",
    "body": "This is a test email body."
  }'
