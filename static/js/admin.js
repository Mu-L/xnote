/*
 * @Author       : xupingmao
 * @email        : 578749341@qq.com
 * @Date         : 2023-11-18 22:14:37
 * @LastEditors  : xupingmao
 * @LastEditTime : 2024-05-03 14:55:44
 * @FilePath     : /xnote/static/js/admin.js
 * @Description  : 后台管理脚本
 */

/**
 * @typedef {import('./xnote-ui/docs.js')}
 */
var AdminView = {}
xnote.admin = AdminView;

// 查看主数据
AdminView.viewMainRecord = function (target) {
    var url = $(target).attr("data-url");
    xnote.http.get(url, function (resp) {
        if (resp.success) {
            xnote.showTextDialog("主数据详情", resp.data);
        } else {
            xnote.toast(resp.message);
        }
    })
}

// 安装python库
AdminView.installPythonLib = function (target) {
    var libName = $(target).attr("data-lib-name");
    xnote.confirm("确认要安装" + libName + "吗?", function () {
        var params = {
            lib_name: libName
        };
        xnote.http.post("/system/install_python_lib", params, function (resp) {
            if (resp.success) {
                xnote.toast("安装成功");
                window.location.reload();
            } else {
                xnote.alert("安装失败:" + resp.message);
            }
        });
    });
};