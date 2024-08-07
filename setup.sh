#!/bin/bash

# 设置环境名称
ENV_NAME="charater-chat-llm-env"

# 检查是否安装了 Conda
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found. Please install Conda and try again."
    exit 1
fi

# 检查环境是否已存在
if conda env list | grep -q $ENV_NAME
then
    echo "Environment $ENV_NAME already exists. Do you want to remove it and create a new one? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        conda env remove --name $ENV_NAME
    else
        echo "Setup aborted. Please use a different environment name or remove the existing environment manually."
        exit 1
    fi
fi

# 创建新的 Conda 环境
echo "Creating new Conda environment: $ENV_NAME"
conda env create -f environment.yml

# 激活环境
echo "Activating environment: $ENV_NAME"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# 检查是否成功激活环境
if [ $? -ne 0 ]; then
    echo "Failed to activate Conda environment. Please check your Conda installation."
    exit 1
fi

echo "Environment setup completed successfully!"
echo "To activate this environment, use: conda activate $ENV_NAME"