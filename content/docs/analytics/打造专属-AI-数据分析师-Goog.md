---
title: '打造专属 AI 数据分析师：Google Analytics MCP 完整配置指南'
---

在日常的独立开发和业务运营中，数据复盘是一项高频且耗时的基础工作。如果每次都需要手动打开统计后台寻找具体的流量面板，会极大地打断工作心流。这篇文章我们将探讨如何基于官方方案（相关技术文档：[https://github.com/googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp) ），通过配置 Google Analytics MCP，让 AI 直接读取并分析你的网站业务数据。

## 前期准备与环境依赖

在正式开始对接之前，我们需要先搞定基础的运行环境。Google Analytics MCP 的核心逻辑是基于 Python 生态构建的。为了更直观地对比环境要求，我整理了以下核心依赖配置清单：

| 依赖模块 | 核心要求 | 作用说明 |
| --- | --- | --- |
| **Python** | 版本必须 **> 3.10** | 整体 MCP 服务的底层运行环境 |
| **pipx** | 需配置全局可用 | 负责独立运行和管理 Python 命令行工具 |

### Python 与 pipx 配置

首先，你必须检查本地的 Python 环境，务必确保 **Python 版本大于 3.10**。检查无误后，我们需要安装包管理工具 pipx。如果在安装过程中遇到阻碍，可以直接查阅官方指引（[https://pipx.pypa.io/stable/#install-pipx](https://pipx.pypa.io/stable/#install-pipx) ）。

环境配置完成后，如何验证其可用性？我建议直接在终端运行以下测试命令：

```bash
pipx run cowsay -t moooooo

```
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/283b055f15a94bd2.jpg)

只要终端成功打印出对应的字符画反馈，就说明你的底层运行环境已经完全就绪。

## Google Cloud 核心配置

这一步是打通数据链路的核心枢纽。我们需要在 Google Cloud Console 中配置权限，为 AI 提供合法调取网站流量数据的底层通道。

### 启用必要 API

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f9c872608c7d7c72.jpg)

你需要登录 Google Cloud 并手动启用以下两个关键的 API 接口：

1. **Google Analytics Data API**：处理具体数据查询的核心接口（[https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com) ）。
2. **Google Analytics Admin API**：处理管理权限的接口（[https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com) ）。

直接打开上述地址，点击页面上的“启用”按钮即可。

### 配置 OAuth 客户端并获取凭证

API 启用后，进入授权概览页面（[https://console.cloud.google.com/auth/overview](https://console.cloud.google.com/auth/overview) ）。在这里，你需要选择或者创建一个客户端以获取系统鉴权密钥。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/23665f76e4327a2e.jpg)

创建完成后，系统会提供一个 JSON 格式的密钥文件。**请务必下载并妥善保存在本地计算机上**，这是后续验证身份的唯一凭据。

## 授权与本地环境配置

为了让本地开发机能够安全地与 Google Cloud 通信，我们需要安装官方提供的命令行工具并完成本地授权登录。

### 安装并配置 gcloud CLI

根据你使用的操作系统，前往官方文档（[http://cloud.google.com/sdk/docs/install](http://cloud.google.com/sdk/docs/install) ）查看对应的安装方式。

以我使用的 Mac 环境为例，操作步骤非常直接：

1. 下载对应的压缩包。
2. 解压文件。
3. 通过终端进入解压后的 `google-cloud-sdk` 目录。
4. 运行 `./install.sh` 命令，随后一路回车确认即可完成部署。

### 执行授权命令

CLI 工具安装完毕后，接下来要将你前面下载的 JSON 密钥文件与本地机器绑定。在终端执行以下命令，请注意，必须把代码中的 `YOUR_CLIENT_JSON_FILE` 替换为你刚刚下载的 JSON 密钥文件的绝对路径：

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform \
  --client-id-file=YOUR_CLIENT_JSON_FILE

```

敲击回车后，系统会自动调用浏览器弹出一个网页让你进行 Google 账号的安全登录确认。授权通过后，终端会返回一段凭证所在的本地路径。**这个路径是接下来配置 MCP 的关键参数，请立即复制这段路径备用**。

## MCP 核心环境变量配置

到了最后一步，我们需要在本地的 MCP 配置文件中填入前置步骤获取的凭证与项目信息，彻底打通整个数据问答链路。

找到你的 MCP 配置文件所在位置，在其中加入 `analytics-mcp` 的核心配置参数。你需要手动替换以下两个关键变量：

* **PATH_TO_CREDENTIALS_JSON**：替换为你在上一步授权登录后，终端返回并要求你复制的那个凭证路径。
* **YOUR_PROJECT_ID**：打开你之前下载的客户端 JSON 密钥文件，在里面找到 `project_id` 字段，将对应的值填入这里。

具体的标准 JSON 配置结构如下：

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "pipx",
      "args": [
        "run",
        "analytics-mcp"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "PATH_TO_CREDENTIALS_JSON",
        "GOOGLE_PROJECT_ID": "YOUR_PROJECT_ID"
      }
    }
  }
}

```

## 总结

保存配置并重启你的 AI 客户端程序。完成这些操作后，你的业务数据查询工作流就彻底升级了。你不再需要刻意去寻找各个数据平台的入口，直接像和同事沟通一样，用大白话向 AI 提问即可了解你的网站运营状况。这种自动化的工作流不仅极大降低了运维成本，也能让你把核心精力释放到更高价值的业务决策上。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/773b46a261f5e192.jpg)
