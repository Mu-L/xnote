import time
import typing
import requests
import json

from xnote.core import xconfig, xmanager
from .base_model import BaseRequest, OpenApiRegistry, BaseResponse
from xnote.service.system_meta_service import SystemMetaEnum
from .dao import SystemSyncAppDao

def invoke_remote_api(request: BaseRequest) -> BaseResponse:
    app_key = xconfig.WebConfig.cluster_node_id
    app_info = SystemSyncAppDao.get_by_app_key(app_key=app_key)
    if app_info is None:
        raise Exception(f"app_info not found, app_key={app_key}")
    request.build(app_key, app_info.app_secret)
    request.validate()
    http_data = json.dumps(request)
    leader_base_url = SystemMetaEnum.leader_base_url.meta_value
    if xconfig.IS_TEST:
        resp = xmanager.request("/open_api/server", method="POST", data=http_data)
        resp_dict = json.loads(str(resp.data, encoding="utf-8"))
    else:
        resp = requests.post(url=f"{leader_base_url}/open_api/server", data=http_data)
        resp_dict = json.loads(resp.text)
    resp_obj = BaseResponse.from_dict(resp_dict)
    resp_sig = resp_obj.calc_signature(app_info.app_secret)
    if not resp_obj.success:
        return resp_obj
    if resp_obj.signature != resp_sig:
        raise Exception(f"invalid response signature, remote={resp_obj.signature}, local={resp_sig}")
    return resp_obj



