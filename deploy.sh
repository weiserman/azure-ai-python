#!/bin/bash
./package.sh
RESOURCEGROUPNAME=main-resources
FUNCTIONAPPNAME=main-pnp-linux-function-app
ZIPPATH=package.zip
az functionapp deployment source config-zip -g "$RESOURCEGROUPNAME" -n "$FUNCTIONAPPNAME" --src "$ZIPPATH" --build-remote true
