# AstroServerControl 在线对《ASTRONEER》专用服务器进行管理

AstroServerControl 可以通过专用服务器的RCON端口连接并管理任意服务器（前提是拥有RCON密钥）。将其部署到任意服务器即可使用任意设备访问，在任意地方管理您的服务器。此外，AstroServerControl提供本地版，只需单独下载`ServerController.py`即可在本地操作远端服务器。

### 功能

包括但不限于：
- 切换游戏存档
- 重启或关闭服务器
- 查看和管理玩家
- 查询服务器各项信息

### 在线版部署教程

Clone 此仓库到本地，并运行`web_controller.py`即可启动flask服务器，默认端口位于`5000`，访问该端口即可进入网页。在“连接服务器”处输入您的服务器IP、RCON端口（默认为1234）、RCON密钥（位于`<服务器目录>/Astro/Saved/Config/AstroServerSettings.ini`中的`ConsolePassword`项）然后点击连接即可使用。

### 本地版部署教程

Clone 此仓库或下载`ServerController.py`到本地并运行即可，同样填入IP、端口、密钥即可连接服务器。

### 依赖
- `Flask`（仅在线版）
- `contextlib`
