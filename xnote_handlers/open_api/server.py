import web
import json

from xnote.open_api.server import BaseRequest, invoke_local_api, SuccessResponse, register_api

class ServerHandler:

    def POST(self):
        data:bytes = web.data()
        data_dict = json.loads(data.decode("utf-8"))
        request = BaseRequest.from_dict(data_dict)
        return invoke_local_api(request)


def ping_method(request: BaseRequest):
    return SuccessResponse("success")

register_api("test.ping", ping_method)

xurls = (
    r"/open_api/server", ServerHandler,
)
