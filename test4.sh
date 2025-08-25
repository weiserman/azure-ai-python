#!/bin/bash
PROTOCOL=https
HOST=main-pnp-linux-function-app.azurewebsites.net
PORT=443
curl -v -X GET "$PROTOCOL://$HOST:$PORT/api/test"
