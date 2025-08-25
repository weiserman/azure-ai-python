import json
import azure.functions as func
def main(req: func.HttpRequest) -> func.HttpResponse:
    resp = {
        "status": "success",
        "message": "test"
    }
    return func.HttpResponse(
        json.dumps(resp),
        status_code=200,
        mimetype="application/json"
    )
