import hmac
import hashlib
from xutils.base import BaseDataRecord
from xutils import dateutil, textutil


class Constants:
    max_time_gap_ms = 5 * 60 * 1000


class BaseRequest(BaseDataRecord):
    def __init__(self):
        self.data = ""
        self.api_name = ""
        self.timestamp = 0 # 时间戳, 5分钟以内
        self.request_id = "" # 随机字符串
        self.data = ""
        self.signature = "" # HMAC-SHA256(AppSecret + timestamp + nonce + data)
        self.app_key = ""


    def calc_signature(self, app_secret: str) -> str:
        sign_str = self.app_key + str(self.timestamp) + self.request_id + self.data
        hmac_obj = hmac.new(
            key=app_secret.encode("utf-8"),
            msg=sign_str.encode("utf-8"),
            digestmod=hashlib.sha256
        )
        # 转为十六进制字符串（大小写不敏感，服务端校验时需统一格式）
        signature = hmac_obj.hexdigest().lower()  # 推荐转为小写，避免大小写不一致问题
        return signature

    def build(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.request_id = textutil.create_uuid()
        self.timestamp = dateutil.timestamp_ms()
        self.signature = self.calc_signature(app_secret)

    def validate(self):
        assert self.api_name != ""
        assert self.app_key != ""
        assert self.signature != ""
        assert self.timestamp != 0
        assert self.request_id != ""

    def validate_remote(self, app_secret: str) -> str:
        ts = dateutil.timestamp_ms()
        if self.api_name == "":
            return "invalid api_name"
        
        if self.app_key == "":
            return "invalid app_key"
        
        if self.request_id == "":
            return "invalid request_id"
        
        if abs(ts - self.timestamp) >= Constants.max_time_gap_ms:
            return "invalid timestamp"
        
        signature = self.calc_signature(app_secret)
        if signature != self.signature:
            return "invalid signature"
        
        return ""

class BaseResponse(BaseDataRecord):
    def __init__(self):
        self.code = "success"
        self.success = True
        self.data = ""
        self.message = ""
        self.signature = "" # 用于验证数据完整性
        self.request_id = ""

    def calc_signature(self, app_secret: str) -> str:
        sign_str = self.request_id + self.data
        hmac_obj = hmac.new(
            key=app_secret.encode("utf-8"),
            msg=sign_str.encode("utf-8"),
            digestmod=hashlib.sha256
        )
        # 转为十六进制字符串（大小写不敏感，服务端校验时需统一格式）
        signature = hmac_obj.hexdigest().lower()  # 推荐转为小写，避免大小写不一致问题
        return signature
    
    def build(self, app_secret: str):
        if self.signature != "":
            return
        self.signature = self.calc_signature(app_secret)

def FailedResponse(code: str, message: str):
    resp = BaseResponse()
    resp.success = False
    resp.code = code
    resp.message = message
    return resp
    
def SuccessResponse(data: str):
    resp = BaseResponse()
    resp.success = True
    resp.code = "success"
    resp.message = "success"
    resp.data = data
    return resp

class OpenApiRegistry:
    mappings = {}
