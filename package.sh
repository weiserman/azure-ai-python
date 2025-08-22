#!/bin/bash
rm -rf package.zip
zip -r ./package.zip ./ -x ".venv/*" -x "*/__pycache__/*" -x "*/.gitignore" -x ".gitignore" -x "res/*" -x "./*.sh" -x "local.settings.json" -x "./res/*" -x ".git/*" -x ".github/*"
