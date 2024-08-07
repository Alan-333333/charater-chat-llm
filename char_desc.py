from os import listdir, path, makedirs
from requests.exceptions import RequestException
import json
import os
import requests
import struct
from base64 import b64decode

class char_desc:
    def __init__(self, filename=None):
        self.name = 'Character'
        self.description = None
        self.personality = None
        self.greeting = None
        self.examples = None
        self.creator_notes = None
        self.scenario = None
        self.lorebook = None
        self.dir = 'characters/'
        self.config_dir = 'character_configs/'
        if filename:
            self.load(filename)

    def load(self, name):
        if not name.endswith('.json'):
            name += '.json'
        name = name.replace('\\', '/')
        if '/' not in name and self.config_dir:
            name = self.config_dir + name
        
        try:
            with open(name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._load_json(data)
        except Exception as e:
            print('char_desc:', e)
            return False

    def download(self, url):
        base = 'chub.ai/characters/'
        try:
            o = url.index(base)
            url = url[o+len(base):].split('/')
            url = '/'.join(url[:2])
            print(f"处理后的URL: {url}")
        except ValueError:
            print(f"URL不包含 {base}, 使用原始URL: {url}")
        
        if '/' not in url:
            print("URL格式不正确，无法下载")
            return None

        chub_url = 'https://api.chub.ai/api/characters/download'
        data = {'format': 'tavern', 'fullPath': url}
        print(f"发送POST请求到: {chub_url}")
        print(f"请求数据: {json.dumps(data)}")
        
        try:
            r = requests.post(chub_url, json=data)
            r.raise_for_status()
        except RequestException as e:
            print(f"请求失败: {e}")
            return None

        print(f"请求状态码: {r.status_code}")
        print(f"响应头: {r.headers}")
        
        if r.headers.get('Content-Type') == 'image/png':
            print("接收到PNG图像，尝试解析嵌入的数据")
            png_data = r.content
            character_data = self._load_data(png_data)
            print(f"character_data:{character_data}")
            if character_data:
                print("成功从PNG中提取角色数据")
                
                if 'data' in character_data and 'name' in character_data['data']:
                    character_name = character_data['data']['name'].replace(' ', '_')
                    
                    # 保存JSON文件
                    json_filename = f"{character_name}.json"
                    json_filepath = os.path.join(self.config_dir, json_filename)
                    os.makedirs(self.config_dir, exist_ok=True)
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(character_data, f, ensure_ascii=False, indent=4)
                    print(f"角色数据已保存到: {json_filepath}")
                    
                    # 保存PNG图片
                    png_filename = f"{character_name}.png"
                    png_filepath = os.path.join(self.dir, png_filename)
                    os.makedirs(self.dir, exist_ok=True)
                    with open(png_filepath, 'wb') as f:
                        f.write(png_data)
                    print(f"原始PNG图片已保存到: {png_filepath}")
                    
                    # 更新实例的属性
                    self._load_json(character_data['data'])
                    
                    return character_data
                else:
                    print("无法保存文件：角色名称不存在于数据中")
                    return None
            else:
                print("无法从PNG中提取有效的角色数据")
                return None
        else:
            print(f"意外的内容类型: {r.headers.get('Content-Type')}")
            print("响应内容的前1000个字符:")
            print(r.text[:1000])
            return None

    def _load_data(self, data):
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return None
        offset = 8
        while offset < len(data):
            l = struct.unpack(">I",data[offset:offset+4])[0]
            offset += 4
            if data[offset:offset+4] != b'tEXt':
                offset += l+8
                continue
            offset += 4
            if data[offset:offset+6] != b'chara\x00':
                offset += l+4
                continue
            offset += 6
            text = b64decode(data[offset:offset+l-6]).decode('UTF-8')
            return json.loads(text)
        return None

    def list(self):
        lst = []
        try:
            lst = [f for f in listdir(self.config_dir) if f.endswith('.json')]
        except:
            pass
        return [f.rstrip('.json') for f in lst]

    def _load_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        if 'data' in data:
            data = data['data']
        self.name = data.get('name')
        self.description = data.get('description')
        self.scenario = data.get('scenario')
        self.personality = data.get('personality')
        self.greeting = data.get('first_mes')
        alt_greetings = data.get('alternate_greetings')
        if alt_greetings and not isinstance(alt_greetings, str):
            if self.greeting:
                alt_greetings.insert(0, self.greeting)
            self.greeting = alt_greetings
        mes_example = data.get('mes_example')
        if mes_example:
            split = '<START>'
            mes_example = mes_example.split(split)
            self.examples = []
            for m in mes_example:
                m = m.strip()
                if not m:
                    continue
                self.examples.append(split+'\n'+m)
        else:
            self.examples = None
        self.creator_notes = data.get('creator_notes')
        character_book = data.get('character_book')
        if character_book:
            self.lorebook = lorebook()
            self.lorebook.load_json(character_book)
        return data  # 返回整个数据字典，而不是布尔值
    
class lorebook:
    def __init__(self):
        self.entries = []

    def load_json(self, data):
        if isinstance(data, dict):
            self.entries = data.get('entries', [])
        elif isinstance(data, list):
            self.entries = data