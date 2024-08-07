import re
import html
import deepl

translator = deepl.Translator("your deepl key")

def translate_to_chinese(text: str) -> str:
    # 第一步：将中文翻译成英文
    english_text = translator.translate_text(text, target_lang="EN-US")
    
    # 第二步：将英文翻译回中文
    chinese_text = translator.translate_text(str(english_text), target_lang="ZH")
    
    # 清理结果
    result = clean_translation(str(chinese_text))
    
    return result

def clean_translation(text: str) -> str:
    # 移除中文字符之间的空格
    result = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    
    # 移除中文和标点符号之间的空格
    result = re.sub(r'([\u4e00-\u9fff])\s+([.,，。！？~、：])', r'\1\2', result)
    result = re.sub(r'([.,，。！？~、：])\s+([\u4e00-\u9fff])', r'\1\2', result)
    
    return html.unescape(result)

# 使用示例
# original_text = '*真由美听着你的命令，立即将她的细瘦的双腿夹住你的头，紧紧地将脸部夹在她的私处中。她将自己的阴部对着你的嘴，温暖的湿润液体开始洒落在你的唇上和舌头上，味道浓郁、甜腻，让你感到一股冲动。*"哥哥，我的淫水真多！来嗑我吧！舔舐我这里，吸吮我这里！让我感到痒痒痒痒痒痒..."*她的娇小身体开始不自觉地性欲极强地扭动着，对你的舔舐和吸吮做出回应，呻吟声不断escalate。*'

# translated_text = translate_through_english(original_text)
# print(translated_text)