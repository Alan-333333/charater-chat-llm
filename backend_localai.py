from backend import backend
import requests
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class backend_localai(backend):
    def __init__(self, api_url, model_name, max_context_length=None):
        super().__init__()
        if not api_url.endswith('/'):
            api_url += '/'
        self.api_url = api_url + 'v1/'
        self.model_name = model_name

        logger.info(f"Initializing LocalAIBackend with API URL: {self.api_url}")

        if max_context_length:
            self.max_context_length = max_context_length
        else:
            self.max_context_length = self._get_max_context_length()

        if not self._validate_model():
            raise ValueError(f"Model '{self.model_name}' not found or not available.")

    def _get_max_context_length(self):
        try:
            # 尝试直接获取模型信息
            r = requests.get(f"{self.api_url}models/{self.model_name}")
            if r.status_code == 200:
                logger.info(f"Successfully fetched model details for {self.model_name}")
                return r.json().get('max_seq_len', 2048)
            
            # 如果上面失败，尝试获取所有模型信息
            r = requests.get(f"{self.api_url}models")
            if r.status_code == 200:
                models = r.json().get('data', [])
                for model in models:
                    if model['id'] == self.model_name:
                        logger.info(f"Found model {self.model_name} in models list")
                        return model.get('max_seq_len', 2048)
            
            logger.warning(f"Could not fetch max_seq_len for model {self.model_name}. Using default value.")
            return 2048  # 默认值
        except Exception as e:
            logger.error(f'Error getting max context length: {str(e)}. Using default.')
            return 2048  # 默认值

    def _validate_model(self):
        try:
            r = requests.get(f"{self.api_url}models")
            if r.status_code != 200:
                logger.error(f"Error fetching models: HTTP {r.status_code}")
                return False

            models = r.json().get('data', [])
            model_exists = any(model['id'] == self.model_name for model in models)
            if model_exists:
                logger.info(f"Model {self.model_name} found in available models")
            else:
                logger.warning(f"Model {self.model_name} not found in available models")
            return model_exists
        except Exception as e:
            logger.error(f"Error validating model: {str(e)}")
            return False

    def tokens_count(self, text):
        words = re.findall(r'\w+', text)
        return int(len(words) * 1.3)

    def generate(self, prompt, stop=None, on_stream=None):
        url = f"{self.api_url}chat/completions"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": getattr(self, 'temperature', 0.7),
            "max_tokens": getattr(self, 'max_length', 150),
            "top_k": getattr(self, 'top_k', 0),
            "top_p": getattr(self, 'top_p', 0.95),
            "presence_penalty": getattr(self, 'rep_pen', 1.1) - 1,
            "frequency_penalty": 0,
            "repeat_penalty": getattr(self, 'rep_pen', 1.1),
            "typical_p": getattr(self, 'typical', 1.0),
            "stream": bool(on_stream),
        }

        if stop:
            data["stop"] = stop
        if getattr(self, 'min_p', 0) > 0:
            data["min_p"] = self.min_p
        if getattr(self, 'rep_pen_range', 0):
            data["repeat_last_n"] = self.rep_pen_range

        logger.debug(f"Sending request to {url} with data: {json.dumps(data, indent=2)}")

        try:
            if on_stream:
                response = requests.post(url, headers=headers, json=data, stream=True)
                response.raise_for_status()
                
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8').split('data: ')[1])
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    on_stream(content, False, len(full_response))
                                    if self._cancel:
                                        break
                        except json.JSONDecodeError:
                            continue
                
                # 在流式响应结束后，调用一次 on_stream，表示这是最后一块内容
                on_stream("", True, len(full_response))
                return None  # The full response has been streamed
            else:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                logger.debug(f"Received response: {json.dumps(result, indent=2)}")
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    logger.warning("No choices in the response")
                    return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in API request: {str(e)}")
            raise  # 重新抛出异常，让调用者知道发生了错误
    def unload(self):
        # 如果需要进行任何清理操作，可以在这里实现
        pass

# 使用示例
# if __name__ == "__main__":
#     try:
#         logger.info("Initializing LocalAIBackend...")
#         backend = backend_localai("http://localhost:8080", "l3-8b-stheno-v3.2-iq-imatrix")
#         logger.info("Model validated successfully.")

#         # 非流式使用
#         logger.info("Generating response...")
#         response = backend.generate("你好")
#         logger.info(f"Response received: {response}")

#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")