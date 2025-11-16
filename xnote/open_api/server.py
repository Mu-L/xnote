import time
import xutils
import web
import json
from .base_model import BaseRequest, BaseResponse, OpenApiRegistry, FailedResponse, SuccessResponse
from .dao import SystemSyncAppDao

def register_api(api_name: str, handler):
    OpenApiRegistry.mappings[api_name] = handler


def invoke_local_api(request: BaseRequest):
    app_info = SystemSyncAppDao.get_by_app_key(request.app_key)
    if app_info is None:
        return FailedResponse(404, f"app_key {request.app_key} not found")
    
    validate_error = request.validate_remote(app_info.app_secret)
    if validate_error != "":
        return FailedResponse(404, f"validate error: {validate_error}")

    api_name = request.api_name
    handler = OpenApiRegistry.mappings[api_name]
    if handler == None:
        return FailedResponse(404, f"api_name {api_name} not found")
    
    resp = handler(request)
    if not isinstance(resp, BaseResponse):
        return FailedResponse(500, f"invalid response, type {type(resp)}")
    
    resp.build(app_info.app_secret)
    return resp
