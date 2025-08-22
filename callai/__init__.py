import azure.functions as func
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    ################################################################################
    # azure document intelligence ocr webservice url
    ################################################################################
    wsurl = "http://localhost:1234/api/ocr"
    ################################################################################
    # email input parameters
    ################################################################################
    header = req.params.get('header')
    subject = req.params.get('subject')
    recipient = req.params.get('recipient')
    body = req.params.get('body')
    # Try to get from JSON body if not present in query
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = None
    if req_body:
        if not header:
            header = req_body.get('header')
        if not subject:
            subject = req_body.get('subject')
        if not recipient:
            recipient = req_body.get('recipient')
        if not body:
            body = req_body.get('body')
    ################################################################################
    # parameter validation
    ################################################################################
    # Standard validation
    import re
    import json
    errors = []
    if not header:
        errors.append("Missing 'header' parameter.")
    if not subject or not subject.strip():
        errors.append("Missing or empty 'subject' parameter.")
    if not recipient or not recipient.strip():
        errors.append("Missing or empty 'recipient' parameter.")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
        errors.append("Invalid email format for 'recipient'.")
    if not body or not body.strip():
        errors.append("Missing or empty 'body' parameter.")
    if errors:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "Parameter validation failed: " + "; ".join(errors)
            }),
            status_code=400,
            mimetype="application/json"
        )

    ################################################################################
    # azure document intelligence ocr  call
    ################################################################################
    # Prepare payload for stub OCR call
    ocr_payload = {
        "header": header,
        "subject": subject,
        "recipient": recipient,
        "body": body
    }
    try:
        response = requests.post(wsurl, json=ocr_payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "Invalid URL provided."
            }),
            status_code=400,
            mimetype="application/json"
        )
    except requests.exceptions.Timeout:
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "Request to the provided URL timed out."
            }),
            status_code=504,
            mimetype="application/json"
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": f"Failed to fetch the URL: {str(e)}"
            }),
            status_code=502,
            mimetype="application/json"
        )

    # Try to parse OCR response as JSON, fallback to text
    try:
        ocr_result = response.json()
    except Exception:
        ocr_result = response.text

    return func.HttpResponse(
        json.dumps({
            "status": "success",
            "message": "Request processed successfully.",
            "ocr_result": ocr_result
        }),
        status_code=response.status_code,
        mimetype="application/json"
    )
