# RWKV_QQBot_BackEnd
 A Python QQ robot backend based on the Shamrock framework, which is used to connect large language models RWKV to QQ.
 
 **- 一个基于Shamrock框架的Python QQ机器人后端，用于将大语言模型RWKV接入QQ。**
 **- 本项目支持任意符合OpenAI API规范的后端，但需要修改配置文件填写API key和Base url**
 **- 本项目采用Quart框架，网络操作均为异步操作，提高响应效率，支持并发！**

![license](https://shields.io/badge/license-GNU%20General%20Public%20License%20v3.0-green)
[![Python Version](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/downloads/release)

![GitHub last commit](https://img.shields.io/github/last-commit/yuunnn-w/RWKV_QQBot_BackEnd)

***

## 使用方法

### 1. 安装Shamrock

在安卓手机或虚拟机上安装Shamrock，教程请参考 [Shamrock Getting Started Guide](https://yuyue-amatsuki.github.io/OpenShamrock/guide/getting-started.html)。

这里作者推荐采用国产开发板香橙派[OrangePi 3b](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-3B.html)进行部署，该开发板无BootLoader锁，获取root权限仅需安装[Magisk](https://github.com/topjohnwu/Magisk/releases)官网最新Release的版本，然后点击直接安装即可自动修补boot获取root权限，简单快捷。

### 2. 配置Shamrock

在Shamrock配置文件中添加上报HTTP服务器的IP和Port等配置选项。IP需要填写运行本Bot的机器的IP和Port。作者在内网环境下运行Bot和Shamrock框架，所以填写的是内网IP。

注意，Shamrock中的一些重要的配置如下：
1. 主动HTTP端口填写5700（即本Bot去访问Shamrock的端口）。
2. 回调HTTP地址填写本Bot运行的地址和端口（端口默认5701）。
3. 开启OneBot标准的HTTPAPI回调选项。
4. 开启HTTPAPI回调的消息格式选项。
5. 推荐开启强制QQ使用平板模式选项。


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

注意，你需要修改QQ配置项为你运行Shamrock框架时登录的QQ账号。另外，还需要指定bot运行的端口，以供Shamrock上报消息等。具体的配置请你仔细阅读 `config.ini` 文件。

理论上Shamrock的请求IP可以直接填写域名，如果你的机器内网不互通的话，可以考虑进行内网穿透并解析到指定域名。

### 6. 安装AI00 RWKV Server

请参考[AI00 RWKV Server](https://github.com/cgisky1980/ai00_rwkv_server)进行安装。

**RWKV5模型下载：**  
1.5B大小的模型：[RWKV-5-World-1B5-v2-20231025-ctx4096.pth](https://huggingface.co/BlinkDL/rwkv-5-world/blob/main/RWKV-5-World-1B5-v2-20231025-ctx4096.pth)  
3B大小的模型：[RWKV-5-World-3B-v2-20231118-ctx16k.pth](https://huggingface.co/BlinkDL/rwkv-5-world/resolve/main/RWKV-5-World-3B-v2-20231118-ctx16k.pth?download=true)     
7B大小的模型：[RWKV-5-World-7B-v2-20240128-ctx4096.pth](https://huggingface.co/BlinkDL/rwkv-5-world/resolve/main/RWKV-5-World-7B-v2-20240128-ctx4096.pth?download=true)。

**如果你的显存大于等于8G，上面三个模型你都可以直接运行。但你需要在ai00中指定NF4量化，量化方法是把 `ai00_rwkv_server/assets/configs/Config.toml` 配置文件中的quant项改为26，然后将quant_type选项改为NF4即可。**  

```
# 配置文件修改示例
quant = 26
quant_type = "NF4"
```

**AI00要求模型格式为.st结尾的safetensors格式权重，你可以运行 `converter.exe` 脚本来将.pth格式的模型权重转换为.st格式的权重，例如：**
```
converter.exe --input RWKV-5-World-7B-v2-20240128-ctx4096.pth
```

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

**另，输入 `lock on` 可以给bot上锁，此时bot只会响应私聊对话，拒绝群聊对话。再次输入 `lock off` 可以解锁。注意，这个功能仅限配置文件中指定的Admin_QQ账号使用。**  

***

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。请参阅 [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html) 获取更多详细信息。

## 引用

- [Shamrock Framework](https://yuyue-amatsuki.github.io/OpenShamrock/guide/getting-started.html)
- [AI00 RWKV Server](https://github.com/cgisky1980/ai00_rwkv_server)

