import re

def process_translated_text(text: str) -> str:
    """
    处理翻译后的文本，移除多余的空格和标签。

    参数:
    text (str): 需要处理的文本

    返回:
    str: 处理后的文本
    """
    # 移除标签
    text = re.sub(r'</?(?:keep|translate)>', '', text)
    
    # 移除中文字符之间的空格
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    
    # 移除中文和标点符号之间的空格
    text = re.sub(r'([\u4e00-\u9fff])\s+([.,，。！？~、：])', r'\1\2', text)
    text = re.sub(r'([.,，。！？~、：])\s+([\u4e00-\u9fff])', r'\1\2', text)

    # 确保 * 和引号周围没有多余的空格
    text = re.sub(r'\s*\*\s*', '*', text)
    text = re.sub(r'\s*"\s*', '"', text)
    
    # 移除所有 "(注意...)" 格式的提示
    text = re.sub(r'\(注意：.*?\)\s*', '', text, flags=re.DOTALL)
    return text

# 如果需要，可以在这里添加更多的辅助函数