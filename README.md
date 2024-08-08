# Character Chat LLM

这是一个基于大型语言模型的角色扮演聊天应用。它允许用户与预定义的角色进行对话，支持多种语言模型后端，并提供了翻译功能。

## 功能特点

- 多角色支持：包括 Mayumi、Reiko、Your_Oblivious_Mother 等多个预定义角色
- 灵活的后端：支持多种语言模型，包括 LocalAI、Baichuan、LLaMA 等
- 实时翻译：使用 DeepL API 进行混合语言翻译
- Web 界面：使用 Flask 提供简单的聊天界面
- Docker 支持：便于部署和扩展


## 依赖

本项目主要依赖于 [LocalAI](https://github.com/mudler/LocalAI)，这是一个强大的本地运行 AI 模型的工具。在使用本项目之前，请确保你已经正确安装和配置了 LocalAI。

## 安装

### 使用 Docker（推荐）

1. 克隆仓库：
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. 构建 Docker 镜像：
   ```
   docker build -t charater-chat-llm .
   ```

3. 运行 Docker 容器：
   ```
   docker run -d -p 5000:5000 -e LOCALAI_SERVICE_URL=http://host.docker.internal:8080 charater-chat-llm
   ```

   注意：确保 LocalAI 服务正在运行，并且可以通过设置的 URL 访问。

### 本地安装

#### 方法 1: 使用 Conda（推荐）

1. 克隆仓库并进入目录：
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. 使用提供的 setup.sh 脚本创建和配置 Conda 环境：
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

   这个脚本会自动创建名为 "charater-chat-llm-env" 的 Conda 环境，并安装所需的依赖。

3. 激活环境：
   ```
   conda activate charater-chat-llm-env
   ```

#### 方法 2: 使用 pip

1. 克隆仓库并进入目录：
   ```
   git clone https://github.com/Alan-333333/charater-chat-llm
   cd character-chat-llm
   ```

2. 创建并激活虚拟环境（可选但推荐）：
   
   ```
   # 在 Linux 或 macOS 上
   python -m venv venv
   source venv/bin/activate 
	
   # 或在 Windows 上
   venv\Scripts\activate  
  
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```


## 使用方法

1. 确保 LocalAI 服务正在运行。

2. 启动应用：
   ```
   python chat_api.py
   ```

3. 在浏览器中访问 `http://localhost:5000` 开始聊天。

## 配置

- 环境变量：
  - `LOCALAI_SERVICE_URL`: LocalAI 服务的 URL（默认为 `http://localhost:8080`）

- 角色配置：在 `characters` 目录中添加或修改角色配置文件。

## 项目结构

- `chat_api.py`: 主应用入口
- `backend_localai.py`: LocalAI 后端实现
- `chat.py`: 聊天核心逻辑
- `deepl_translate_mixed_lang.py`: DeepL 翻译功能
- `templates/`: Web 界面模板
- `characters/`: 角色图片
- `character_configs/`: 角色配置文件
- `setup.sh`: 自动化环境设置脚本

## 贡献

欢迎提交问题和拉取请求。
