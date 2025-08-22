import json
import time
import azure.functions as func
import requests
import logging
import os
from typing import BinaryIO, Optional
import re
import base64
import io
import random
import string
# ------------------------------------------------------------------------------
# Azure Document Intelligence: Upload, Analyze, Poll, and Get Result
# ------------------------------------------------------------------------------
def analyze_document_stream(
    file_stream: BinaryIO,
    file_name: str,
    account_name: str,
    container_name: str,
    sas_token: str,
    endpoint: str,
    subscription_key: str,
    model_id: str = "prebuilt-invoice",
    api_version: str = "2024-11-30",
    poll_interval: float = 1.0,
    logger: Optional[logging.Logger] = None
) -> dict:
    """
    Uploads a file to Azure Blob Storage, starts Document Intelligence analysis, polls for completion, and returns the result.
    Args:
        file_stream: BinaryIO or bytes, the file content to upload.
        file_name: Name for the blob in the container.
        account_name: Azure Blob Storage account name.
        container_name: Blob container name.
        sas_token: SAS token for blob upload.
        endpoint: Azure Document Intelligence endpoint (e.g., https://<region>.api.cognitive.microsoft.com).
        subscription_key: Azure Cognitive Services subscription key.
        model_id: Document Intelligence model id (default: prebuilt-invoice).
        api_version: API version (default: 2024-11-30).
        poll_interval: Seconds between polling attempts.
        logger: Optional logger for debug output.
    Returns:
        dict: The analyze result from Document Intelligence.
    """
    if logger is None:
        logger = logging.getLogger("callai.analyze_document_stream")
    # Upload to blob storage
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{file_name}?{sas_token}"
    logger.debug(f"Uploading to blob: {blob_url}")
    upload_headers = {"x-ms-blob-type": "BlockBlob"}
    upload_resp = requests.put(blob_url, headers=upload_headers, data=file_stream)
    if not (200 <= upload_resp.status_code < 300):
        raise RuntimeError(f"Blob upload failed: {upload_resp.status_code} {upload_resp.text}")
    logger.debug("Upload successful.")
    # Start document analysis
    img_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{file_name}"
    analyze_url = f"{endpoint}/documentintelligence/documentModels/{model_id}:analyze?api-version={api_version}"
    analyze_headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    analyze_payload = {"urlSource": img_url}
    logger.debug(f"Starting analysis: {analyze_url}")
    analyze_resp = requests.post(analyze_url, headers=analyze_headers, json=analyze_payload)
    if not (200 <= analyze_resp.status_code < 300):
        raise RuntimeError(f"Analyze start failed: {analyze_resp.status_code} {analyze_resp.text}")
    operation_url = analyze_resp.headers.get("operation-location")
    if not operation_url:
        raise RuntimeError("No operation-location header in analyze response.")
    logger.debug(f"Polling operation: {operation_url}")
    # Poll for completion
    while True:
        poll_headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        poll_resp = requests.get(operation_url, headers=poll_headers)
        if not (200 <= poll_resp.status_code < 300):
            raise RuntimeError(f"Polling failed: {poll_resp.status_code} {poll_resp.text}")
        poll_json = poll_resp.json()
        status = poll_json.get("status")
        logger.debug(f"Status: {status}")
        if status and status.lower() not in ("running", "notstarted"):
            break
        time.sleep(poll_interval)
    logger.debug("Analysis complete.")
    return poll_json
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
################################################################################
# constants
################################################################################
def main(req: func.HttpRequest) -> func.HttpResponse:
    ################################################################################
    logger.debug('--- Incoming request ---')
    logger.debug(f'Headers: {dict(req.headers)}')
    try:
        logger.debug(f'Body: {req.get_body().decode("utf-8", errors="replace")[:2048]}')
    except Exception as e:
        logger.debug(f'Body decode error: {e}')
    ################################################################################
    # Read Azure config from environment variables (UPPERCASE)
    ################################################################################
    AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
    AZURE_CONTAINER_NAME = os.environ.get('AZURE_CONTAINER_NAME')
    AZURE_SAS_TOKEN = os.environ.get('AZURE_SAS_TOKEN')
    AZURE_ENDPOINT = os.environ.get('AZURE_ENDPOINT')
    AZURE_SUBSCRIPTION_KEY = os.environ.get('AZURE_SUBSCRIPTION_KEY')
    AZURE_MODEL_ID = os.environ.get('AZURE_MODEL_ID', 'prebuilt-invoice')
    AZURE_API_VERSION = os.environ.get('AZURE_API_VERSION', '2024-11-30')
    azure_env_errors = []
    for var, val in [
        ("AZURE_ACCOUNT_NAME", AZURE_ACCOUNT_NAME),
        ("AZURE_CONTAINER_NAME", AZURE_CONTAINER_NAME),
        ("AZURE_SAS_TOKEN", AZURE_SAS_TOKEN),
        ("AZURE_ENDPOINT", AZURE_ENDPOINT),
        ("AZURE_SUBSCRIPTION_KEY", AZURE_SUBSCRIPTION_KEY)
    ]:
        if not val:
            azure_env_errors.append(f"Missing required Azure environment variable: {var}")
    if azure_env_errors:
        resp = {
            "status": "error",
            "message": "; ".join(azure_env_errors)
        }
        logger.debug('--- Outgoing response ---')
        logger.debug(resp)
        return func.HttpResponse(
            json.dumps(resp),
            status_code=500,
            mimetype="application/json"
        )
    ################################################################################
    # email input parameters
    ################################################################################
    header = req.params.get('header')
    subject = req.params.get('subject')
    recipient = req.params.get('recipient')
    body = req.params.get('body')
    attachments = None
    # Check if incoming request is JSON if Content-Type is set
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
    # call analyze function
    ################################################################################
    # If attachments exist, call analyze_document_stream with the first one as binary
    analyze_result = None
    if attachments and isinstance(attachments, list) and len(attachments) > 0:
        # Assume attachments are base64-encoded strings (from JSON or multipart)
        try:
            first_attachment_b64 = attachments[0]
            file_bytes = base64.b64decode(first_attachment_b64)
            file_stream = io.BytesIO(file_bytes)
            # Generate a random file name with .bin extension
            rand_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12)) + '.bin'
            analyze_result = analyze_document_stream(
                file_stream=file_stream,
                file_name=rand_name,
                account_name=AZURE_ACCOUNT_NAME,
                container_name=AZURE_CONTAINER_NAME,
                sas_token=AZURE_SAS_TOKEN,
                endpoint=AZURE_ENDPOINT,
                subscription_key=AZURE_SUBSCRIPTION_KEY,
                model_id=AZURE_MODEL_ID,
                api_version=AZURE_API_VERSION,
                logger=logger
            )
        except Exception as e:
            logger.error(f"analyze_document_stream failed: {e}")
            analyze_result = {"status": "error", "message": str(e)}
    else:
        analyze_result = {"status": "error", "message": "No valid attachment found for analysis."}

    resp = {
        "status": "success",
        "message": "Request processed successfully.",
        "analyze_result": analyze_result
    }
    logger.debug('--- Outgoing response ---')
    logger.debug(json.dumps(resp)[:4096])
    return func.HttpResponse(
        json.dumps(resp),
        status_code=200,
        mimetype="application/json"
    )
