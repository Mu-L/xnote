from xutils import jsonutil
from xnote.open_api import register_api, BaseRequest, SuccessResponse, FailedResponse
from .system_sync_instances import LeaderInstance
from .models import ListBinlogRequest, ListDBRequest, ListDBResponse, GetBackupInfoResponse
from xnote.service.system_meta_service import SystemMetaEnum
from xnote_handlers.system.system_sync.models import FileIndexInfo
from xnote_handlers.fs.fs_helper import FileInfoDao

def list_binlog(req: BaseRequest):
    list_req = ListBinlogRequest.from_json(req.data)
    if list_req is None:
        raise Exception("req.data is empty")
    
    result = LeaderInstance.list_binlog(
        last_seq=list_req.last_seq, limit=list_req.limit, include_req_seq=list_req.include_req_seq)
    
    if result.success:
        return SuccessResponse(jsonutil.tojson(result.data))
    else:
        return FailedResponse(result.code, result.message)

def list_db(req: BaseRequest):
    list_req = ListDBRequest.from_json(req.data)
    if list_req is None:
        raise Exception("req.data is empty")
    
    result = LeaderInstance.list_db(last_key=list_req.last_key)
    return SuccessResponse(jsonutil.tojson(result))
    
def get_backup_info(req: BaseRequest):
    result = GetBackupInfoResponse()
    filepath = SystemMetaEnum.db_backup_file.meta_value
    file_info = FileInfoDao.get_by_fpath(filepath)
    if file_info is None:
        return FailedResponse("not_found", "备份文件不存在")
    
    file_index_info = file_info.to_file_index_info()

    result.backup_file = SystemMetaEnum.db_backup_file.meta_value
    result.backup_binlog_id = SystemMetaEnum.db_backup_binlog_id.meta_value_int
    result.backup_file_info = file_index_info
    return SuccessResponse(jsonutil.tojson(result))


def init():
    register_api("system.sync.list_binlog", list_binlog)
    register_api("system.sync.list_db", list_db)
    register_api("system.sync.get_backup_info", get_backup_info)
