# Xnote

[![Build Status](https://travis-ci.org/xupingmao/xnote.svg?branch=master)](https://travis-ci.org/xupingmao/xnote)
[![Coverage Status](https://coveralls.io/repos/github/xupingmao/xnote/badge.svg?branch=master)](https://coveralls.io/github/xupingmao/xnote?branch=master)

xnote是一款功能丰富的个人信息管理系统，提供多种维度的数据管理功能。它有如下特点

- 拥有丰富的数据管理能力，支持笔记、提醒、文件管理
- 自带工具箱，默认提供了大量常用的工具
- 提供扩展能力，用户可以编写各种插件满足自己的需求
- 跨平台，支持Windows、Mac、Linux三大平台，可以在云服务上部署，也可以在本地运行


PS：目前本项目主要目标人群是个人，提供有限的多用户支持

![主页](https://git.oschina.net/xupingmao/xnote/raw/master/screenshots/xnote_v2.1_home.png)

-----
## 项目地址
- [github](https://github.com/xupingmao/xnote)
- [码云](https://gitee.com/xupingmao/xnote)


## 安装运行
- 安装python（支持Python2、3，建议Python3）
- 安装依赖的软件包```python -m pip install -r requirements.txt```
- 启动服务器`python app.py`, 默认1234端口, 浏览器打开http://localhost:1234/ 无需额外配置，初始化的管理员账号是admin/123456
- 可以直接部署在新浪云应用SAE上面
- 如果安装老版本后更新启动失败参考 [数据库迁移](./docs/db_migrate.md)

### 启动参数
- `--data {data_path}` 指定数据存储的data目录，比如`python app.py --data D:/data`
- `--port 1234`启动端口号，注意优先使用环境变量{PORT}设置的端口号，这是为了自适应云服务容器的端口
- `--useUrlencode yes`针对只支持ASCII编码的文件系统开启urlencode转换非ASCII码字符
- `--minthreads {number}` web请求处理线程数


## 主要功能

### 知识管理
- 编辑器支持markdown和富文本两种方式，建议使用markdown
- 提供分组和标签两种方式来组织文档
- 支持文档分享
- 支持按标题和内容搜索
- 基于用户维度进行数据权限隔离

### 任务管理
- 可以快速写文字或者上传图片、文件等
- 提醒有关注、挂起、完成三个状态，基本满足日常工作需求
- 基于用户维度进行数据权限隔离
- 日历功能，暂时比较简单

### 文件管理
- 访问需要管理员权限
- 列表、网格等多种视图模式
- 文件上传下载、创建、删除、重命名、剪切等操作
- 文本编辑器
- 文本内容搜索
- 代码行统计
- WebShell

### 工具箱
- Python文档(pydoc)
- 文本处理(文本对比，代码生成，密码生成)
- 编解码工具(base64,16进制等等)
- 条形码、二维码生成器(barcode)
- 图像处理（合并、拆分、灰度化）

### 插件扩展

由于每个人的需求不同，单一系统很难满足，开发者可以根据自己需要编写插件来扩展系统的功能。具体可以参考文档 [插件扩展](./docs/plugins.md)。

具体特性如下

- 插件中可以监听系统消息，包括笔记、提醒、文件、时间、系统五种类型的消息
- 插件可以通过实现`is_visible`接口显示在笔记、文件、系统等功能的选项入口中
- 插件模板
- 插件访问日志

### 其他特性
- debug模式下自动侦测模块修改并重新加载
- 支持文件下载断点续传,发生网络故障后不用重新下载
- 使用响应式布局，尽量保证PC、移动平台体验一致
- 用户权限，通过Python的装饰器语法，比较方便修改和扩展(见xauth.login\_required)
- 数据库结构自动更新(xtables.py)
- 支持纯ASCII码文件系统（上传文件名会经过urlencode转码）
- 单元测试覆盖率50%以上
- 自定义启动脚本
- 自定义CSS

## 相关文档
- [更新日志](./docs/changelog.md)
- [插件扩展](./docs/plugins.md)
- [搜索扩展](./docs/search_extension.md)
- [文件命令扩展](./docs/commands.md)
- [系统架构](./docs/architecture.md)

## 协议

- GPL

