# Azure Function App (Python)

This is a basic Azure Function App for Python with a "Hello World" HTTP trigger.

## Structure

- `requirements.txt` - Python dependencies
- `host.json` - Global configuration options
- `local.settings.json` - Local development settings
- `HelloWorldFunction/` - Contains the HTTP trigger function

## Running Locally

1. Install the Azure Functions Core Tools and Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the function app:
   ```bash
   func start
   ```
3. Test the endpoint:
   - GET/POST http://localhost:7071/api/HelloWorldFunction?name=YourName

## Running Locally - UV

```
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
nvm use --lts
npm install -g azure-functions-core-tools@4 --unsafe-perm true
func start
```

## Notes
- Make sure you have the Azure Functions Core Tools installed.
- This project uses the v2 runtime and Python worker.
