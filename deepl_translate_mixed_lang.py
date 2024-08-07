import html
import deepl
import time
import re

translator = deepl.Translator("your deepl key")
translation_cache = {}

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'

def translate_to_chinese(text: str) -> str:
    # 使用正则表达式分割文本
    segments = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9\s\'\"]+|[^\u4e00-\u9fffa-zA-Z0-9\s]', text)
    
    result = []
    for segment in segments:
        if is_chinese(segment[0]):
            # 中文段落，直接添加
            result.append(segment)
        elif segment.strip():
            # 非空的非中文段落，需要翻译
            translated = translate_segment(segment)
            result.append(translated)
        else:
            # 空白字符，直接添加
            result.append(segment)
    
    # 处理结果，移除不必要的空格
    final_result = ''.join(result)
    final_result = re.sub(r'\s+([，。！？、：])', r'\1', final_result)  # 移除标点前的空格
    final_result = re.sub(r'([，。！？、：])\s+', r'\1', final_result)  # 移除标点后的空格
    final_result = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', final_result)  # 移除中文之间的空格
    
    return final_result

def translate_segment(segment: str) -> str:
    if segment in translation_cache:
        return translation_cache[segment]

    result = translator.translate_text(segment, target_lang="ZH")
    translated = html.unescape(str(result))
    translation_cache[segment] = translated
    
    return translated

# 使用示例
# start_time = time.time()

# original_texts = [
#     "I just 想玩玩罢了。只是，如果你不 obedie nt to me, I'll definitely report you to the police! You have no choice but to do whatever I say!",
#     "This is a test sentence. 这是一个测试句子。 Another English part.",
#     "Hello! 你好！How are you? 最近还好吗？",
#     "The quick brown fox 快速的棕色狐狸 jumps over 跳过 the lazy dog 懒惰的狗。",
#     "Don't forget to bring your umbrella! 别忘了带伞！It's going to rain. 要下雨了。"
# ]

# for i, original_text in enumerate(original_texts, 1):
#     print(f"\n测试案例 {i}:")
#     print(f"原文: {original_text}")
#     translated_text = translate_to_chinese(original_text)
#     print(f"译文: {translated_text}")

# end_time = time.time()
# execution_time = end_time - start_time
# print(f"\n总翻译耗时: {execution_time:.2f} 秒")