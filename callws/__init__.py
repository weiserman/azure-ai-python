import azure.functions as func
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    wsurl = req.params.get('wsurl')
    if not wsurl:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            wsurl = req_body.get('wsurl')

    if not wsurl:
        return func.HttpResponse(
            "Please pass a wsurl on the query string or in the request body",
            status_code=400
        )

    try:
        response = requests.get(wsurl, timeout=10)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        return func.HttpResponse(
            "Invalid URL provided.",
            status_code=400
        )
    except requests.exceptions.Timeout:
        return func.HttpResponse(
            "Request to the provided URL timed out.",
            status_code=504
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return func.HttpResponse(
            f"Failed to fetch the URL: {str(e)}",
            status_code=502
        )

    return func.HttpResponse(
        response.text,
        status_code=response.status_code,
        mimetype=response.headers.get('Content-Type', 'text/plain')
    )
