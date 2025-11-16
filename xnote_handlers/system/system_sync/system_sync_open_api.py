import json

from xnote.open_api import register_api, BaseRequest, SuccessResponse, FailedResponse
from .system_sync_instances import LeaderInstance
from .models import ListBinlogRequest

def list_binlog(req: BaseRequest):
    list_req = ListBinlogRequest.from_json(req.data)
    if list_req is None:
        raise Exception("req.data is empty")
    
    result = LeaderInstance.list_binlog(
        last_seq=list_req.last_seq, limit=list_req.limit, include_req_seq=list_req.include_req_seq)
    
    if result.success:
        return SuccessResponse(json.dumps(result.data))
    else:
        return FailedResponse(result.code, result.message)


def init():
    register_api("system.sync.list_binlog", list_binlog)
