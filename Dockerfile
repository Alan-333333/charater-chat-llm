# 使用 conda 官方镜像作为基础镜像
FROM continuumio/miniconda3:latest

# 设置工作目录
WORKDIR /app

# 复制 environment.yml 文件
COPY environment.yml .

# 创建 conda 环境
RUN conda env create -f environment.yml

# 激活 conda 环境
SHELL ["conda", "run", "-n", "charater-chat-llm-env", "/bin/bash", "-c"]

# 复制应用代码
COPY . .

# 暴露端口（假设你的应用运行在 5000 端口）
EXPOSE 5000

# 运行应用（请根据你的实际启动命令进行修改）
CMD ["conda", "run", "--no-capture-output", "-n", "charater-chat-llm-env", "python", "chat_api.py"]