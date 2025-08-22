import azure.functions as func
import requests
import logging
import os
################################################################################
# azure logging sample
################################################################################
logger = logging.getLogger('akshay')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.debug('Constructor:begin')
logger.debug('Constructor:end')
def main(req: func.HttpRequest) -> func.HttpResponse:
    ################################################################################
    logger.debug('--- Incoming request ---')
    logger.debug(f'Headers: {dict(req.headers)}')
    try:
        logger.debug(f'Body: {req.get_body().decode("utf-8", errors="replace")[:2048]}')
    except Exception as e:
        logger.debug(f'Body decode error: {e}')
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
    attachments = None
    # Check if incoming request is JSON if Content-Type is set
    import json
    req_content_type = req.headers.get('Content-Type', '').lower().strip()
    # Allow application/json and multipart/form-data
    is_json = req_content_type.startswith('application/json')
    is_multipart = req_content_type.startswith('multipart/form-data')
    if req.method == 'POST' and not (is_json or is_multipart):
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": f"Invalid content type for request: {req_content_type}"
            }),
            status_code=400,
            mimetype="application/json"
        )
    # Try to get from JSON body if not present in query, or from form data if multipart
    req_body = None
    if is_json:
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
            attachments = req_body.get('attachments') if 'attachments' in req_body else None
    elif is_multipart:
        # For multipart, use req.form and req.files
        import base64
        form = req.form
        if not header:
            header = form.get('header')
        if not subject:
            subject = form.get('subject')
        if not recipient:
            recipient = form.get('recipient')
        if not body:
            body = form.get('body')
        # Extract all files for the 'attachments' field and convert to base64
        attachments = []
        # req.files can have multiple files per field name, use getlist if available
        if hasattr(req.files, 'getlist'):
            for file in req.files.getlist('attachments'):
                file_content = file.read()
                b64_content = base64.b64encode(file_content).decode('utf-8')
                attachments.append(b64_content)
        else:
            # fallback: collect all files with key 'attachments' or all files if not grouped
            for file_key in req.files:
                if file_key == 'attachments':
                    file = req.files[file_key]
                    file_content = file.read()
                    b64_content = base64.b64encode(file_content).decode('utf-8')
                    attachments.append(b64_content)
        if not attachments:
            attachments = None
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
    if attachments is not None:
        if is_json:
            if not isinstance(attachments, list):
                errors.append("'attachments' must be a list of base64 strings in JSON requests.")
        elif is_multipart:
            if not isinstance(attachments, list):
                errors.append("'attachments' must be a list of files in multipart requests.")
    if errors:
        resp = {
            "status": "error",
            "message": "Parameter validation failed: " + "; ".join(errors)
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
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
        "body": body,
        "attachments": attachments if attachments is not None else []
    }
    try:
        response = requests.post(wsurl, json=ocr_payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        resp = {
            "status": "error",
            "message": "Invalid URL provided."
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
            status_code=400,
            mimetype="application/json"
        )
    except requests.exceptions.Timeout:
        resp = {
            "status": "error",
            "message": "Request to the provided URL timed out."
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
            status_code=504,
            mimetype="application/json"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        resp = {
            "status": "error",
            "message": f"Failed to fetch the URL: {str(e)}"
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
            status_code=502,
            mimetype="application/json"
        )

    # Check if OCR response is JSON
    content_type = response.headers.get('Content-Type', '').lower().strip()
    if not content_type.startswith('application/json'):
        resp = {
            "status": "error",
            "message": f"Invalid content type from OCR service: {content_type}"
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
            status_code=502,
            mimetype="application/json"
        )
    try:
        ocr_result = response.json()
    except Exception:
        resp = {
            "status": "error",
            "message": "Failed to parse OCR service response as JSON."
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(json.dumps(resp))
        return func.HttpResponse(
            json.dumps(resp),
            status_code=502,
            mimetype="application/json"
        )

    resp = {
        "status": "success",
        "message": "Request processed successfully.",
        "ocr_result": ocr_result
    }
    logger.debug('--- Outgoing response ---')
    logger.debug(json.dumps(resp)[:4096])
    return func.HttpResponse(
        json.dumps(resp),
        status_code=response.status_code,
        mimetype="application/json"
    )
