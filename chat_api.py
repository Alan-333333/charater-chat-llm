from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import json
import logging
from chat import chat
from backend_localai import backend_localai
from deepl_translate_mixed_lang import translate_to_chinese
from text_processor import process_translated_text
import re
import os

app = Flask(__name__)
# 设置日志
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
app.config['JSON_AS_ASCII'] = False

backend = None
chat_instances = {}

# 角色配置
characters = {
    'Mayumi': {
        'image': '/character-chat/character_image/Mayumi.png',
        'user_name': '大哥哥',
        'character_name': '真由美',
        'load_name': 'Mayumi',
    },
    'Reiko': {
        'image': '/character-chat/character_image/Reiko.png',
        'user_name': '弟弟',
        'character_name': '姐姐',
        'load_name': 'Reiko',
    },
    'Your_Oblivious_Mother': {
        'image': '/character-chat/character_image/Your_Oblivious_Mother.png',
        'user_name': '儿子',
        'character_name': '妈妈',
        'load_name': 'Your_Oblivious_Mother',
    },
    'Goldie': {
        'image': '/character-chat/character_image/Goldie.png',
        'user_name': '同学',
        'character_name': '戈尔迪',
        'load_name': 'Goldie',
    },
    'MaidoDism': {
        'image': '/character-chat/character_image/MaidoDism.png',
        'user_name': '主人',
        'character_name': '女仆',
        'load_name': 'MaidoDism',
    },
    'Kayla': {
        'image': '/character-chat/character_image/Kayla.png',
        'user_name': '哥哥',
        'character_name': '凯拉',
        'load_name': 'Kayla',
    },
    'Mia': {
        'image': '/character-chat/character_image/Mia.png',
        'user_name': '你',
        'character_name': '米亚',
        'load_name': 'Mia',
    },
    'Makoto': {
        'image': '/character-chat/character_image/Makoto.png',
        'user_name': '你',
        'character_name': '小南',
        'load_name': 'Makoto',
    },
    'Ann': {
        'image': '/character-chat/character_image/Ann.png',
        'user_name': '你',
        'character_name': '妈妈',
        'load_name': 'Ann',
    },
    'Michiko': {
        'image': '/character-chat/character_image/Michiko.png',
        'user_name': '哥哥',
        'character_name': '妹妹',
        'load_name': 'Michiko',
    },
    'Yoshiko': {
        'image': '/character-chat/character_image/Yoshiko.png',
        'user_name': '同学',
        'character_name': '艾琳老师',
        'load_name': 'Yoshiko',
    }
}

default_character = 'Mayumi'


def contains_english(text):
    # 检查是否包含英文字母
    return bool(re.search('[a-zA-Z]', text))


def get_or_create_chat_instance():
    global backend
    if backend is None:
        localai_url = os.environ.get('LOCALAI_SERVICE_URL', 'http://local-ai:8080')
        backend = backend_localai(
                    localai_url, "l3-8b-stheno-v3.2-iq-imatrix")
        backend.max_length = 1000

    return chat(backend)


def load_character(chat_instance, character):
    if character not in characters:
        app.logger.warning(
            f"Character '{character}' not found, using default character '{default_character}'")
        character = default_character

    app.logger.info(f"Loading character: {characters[character]['load_name']}")
    chat_instance.char.load(characters[character]['load_name'])
    chat_instance.user.name = characters[character]['user_name']

    # 添加强制中文输出的设置
    force_chinese_output(chat_instance)


def force_chinese_output(chat_instance):
    # 方法1：在系统提示中添加中文输出指令
    if chat_instance.system:
        chat_instance.system += "\n请始终使用中文回答所有问题和对话。"
    else:
        chat_instance.system = "请始终使用中文回答所有问题和对话。"

    # 方法2：在角色描述中添加中文输出指令
    chat_instance.char.description += "\n你必须始终使用中文进行对话和回答问题。"

    # 方法3：修改模板以包含中文输出指令
    chinese_instruction = "请注意：所有回答和对话必须使用中文。\n"
    chat_instance.template = chinese_instruction + chat_instance.template

    original_say = chat_instance.say

    def say_with_chinese_check(text, on_stream=None, name='{{user}}', answer_as='{{char}}'):
        response = original_say(text, on_stream, name, answer_as)

        # 检查响应是否包含英文字符
        if contains_english(response):
            # 如果包含英文字符，尝试翻译
            try:
                logging.info(f"Original response: {response}")
                translated_response = translate_to_chinese(response)
                logging.info(f"Translated response: {translated_response}")
                return translated_response
            except Exception as e:
                logging.error(f"Translation failed: {e}")

        return process_translated_text(response)

    chat_instance.say = say_with_chinese_check


@app.route('/')
def serve_chat_page():
    character = request.args.get('character', default_character)

    try:
        chat_instance = get_or_create_chat_instance()
        load_character(chat_instance, character)
    except ValueError as ve:
        app.logger.error(f"ValueError in serve_chat_page: {str(ve)}")
        return redirect(url_for('serve_chat_page', character=default_character))
    except Exception as e:
        app.logger.error(f"Unexpected error in serve_chat_page: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

    try:
        config = {
            'backgroundImage': characters[character]['image'],
            'characterName': characters[character]['character_name'],
            'userName': characters[character]['user_name']
        }
    except KeyError as ke:
        app.logger.error(f"KeyError in serve_chat_page: {str(ke)}")
        app.logger.error(
            f"Character data: {characters.get(character, 'Not found')}")
        return jsonify({"error": f"Invalid character configuration: {str(ke)}"}), 400

    try:
        return render_template('chat.html', config=config, character=character)
    except Exception as e:
        app.logger.error(f"Error rendering template: {str(e)}")
        return jsonify({"error": "Error rendering template"}), 500


@app.route('/start_chat', methods=['GET'])
def start_chat():
    character = request.args.get('character', default_character)
    try:
        chat_instance = get_or_create_chat_instance()
        load_character(chat_instance, character)
        greeting = chat_instance.start()
        return jsonify({"greeting": greeting})
    except Exception as e:
        app.logger.error(f"Error in start_chat: {str(e)}")
        return jsonify({"error": "An error occurred while starting the chat"}), 500


@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.json
    prompt = data.get('prompt')
    character = data.get('character', default_character)

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        chat_instance = get_or_create_chat_instance()
        load_character(chat_instance, character)
        response = chat_instance.say(prompt)
        return json.dumps({"response": response}, ensure_ascii=False)
    except Exception as e:
        app.logger.error(f"Error in chat_api: {str(e)}")
        return jsonify({"error": "An error occurred during the chat"}), 500


@app.route('/change_character', methods=['POST'])
def change_character():
    data = request.json
    new_character = data.get('character')
    try:
        chat_instance = get_or_create_chat_instance()
        load_character(chat_instance, new_character)
        config = {
            'backgroundImage': characters[new_character]['image'],
            'characterName': characters[new_character]['character_name'],
            'userName': characters[new_character]['user_name']
        }
        return jsonify({"success": True, "config": config})
    except Exception as e:
        app.logger.error(f"Error in change_character: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/character_image/<path:filename>')
def serve_character_image(filename):
    return send_from_directory('characters', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
