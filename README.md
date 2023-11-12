# RWKV_QQBot_BackEnd
 A Python QQ robot backend based on the Shamrock framework, which is used to connect large language models RWKV to QQ.
 
 一个基于Shamrock框架的Python QQ机器人后端，用于将大语言模型RWKV接入QQ。

![license](https://shields.io/badge/license-GNU%20General%20Public%20License%20v3.0-green)
[![Python Version](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/downloads/release)

![GitHub last commit](https://img.shields.io/github/last-commit/JiaXinSugar-114514/RWKV_QQBot_BackEnd)

## 使用方法

### 1. 安装Shamrock

在安卓手机或虚拟机上安装Shamrock，教程请参考 [Shamrock Getting Started Guide](https://yuyue-amatsuki.github.io/OpenShamrock/guide/getting-started.html)。

这里作者推荐采用国产开发板香橙派[OrangePi 3b](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-3B.html)进行部署，该开发板无BootLoader锁，获取root权限仅需安装[Magisk](https://github.com/topjohnwu/Magisk/releases)官网最新Release的版本，然后点击直接安装即可自动修补boot获取root权限，简单快捷。

### 2. 配置Shamrock

在Shamrock配置文件中添加上报HTTP服务器的IP和Port等配置选项。IP需要填写运行本Bot的机器的IP和Port。作者在内网环境下运行Bot和Shamrock框架，所以填写的是内网IP。

### 3. 克隆项目

```bash
git clone https://github.com/JiaXinSugar-114514/RWKV_QQBot_BackEnd.git
cd RWKV_QQBot_BackEnd
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 修改配置文件

根据你的需求修改 `config.ini` 配置文件。

### 6. 安装AI00 RWKV Server

请参考[AI00 RWKV Server](https://github.com/cgisky1980/ai00_rwkv_server)进行安装。

### 7. 添加Prompt

在 `prompt` 目录下添加预设的prompt，一个角色的prompt要同时包含 `txt` 和 `json` 后缀的两个配置文件。当然你也可以偷懒使用作者预设的角色进行角色扮演任务。

### 8. 启动服务

```bash
python bot.py
```
### 9. 查看帮助

在QQ群艾特QQbot然后输入help指令即可查看帮助，也可私聊，此时无需艾特。查看帮助示例：

```bash
@QQbot help
```
这里的QQbot是QQ机器人账号的昵称。

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。请参阅 [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html) 获取更多详细信息。

## 引用

- [Shamrock Framework](https://yuyue-amatsuki.github.io/OpenShamrock/guide/getting-started.html)
- [AI00 RWKV Server](https://github.com/cgisky1980/ai00_rwkv_server)
