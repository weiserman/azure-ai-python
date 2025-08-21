import azure.functions as func
def main(req:func.HttpRequest)->func.HttpResponse:
    return func.HttpResponse(f"test foo",status_code=200)
