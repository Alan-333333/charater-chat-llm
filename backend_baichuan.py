from backend import backend
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

class backend_baichuan(backend):
    def __init__(self, model_directory, max_context_length=2048):
        super().__init__()
        self.max_context_length = max_context_length
        
        # 清空 CUDA 缓存
        torch.cuda.empty_cache()
        
        # 检查 CUDA 是否可用
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # 设置 4-bit 量化配置
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        
        # 加载 tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_directory, trust_remote_code=True)
        
        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_directory,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        print(f"Model device: {self.model.device}")
        print(f"Model memory: {self.model.get_memory_footprint() / 1e9:.2f} GB")

        # 如果模型没有自动移到CUDA，手动移动
        if self.model.device.type != 'cuda' and torch.cuda.is_available():
            self.model.to(self.device)
            print("Model manually moved to CUDA")

    def tokens_count(self, text):
        if not isinstance(text, str):
            raise TypeError(f"Expected string input, got {type(text)}")
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            print(f"Error in tokens_count: {e}")
            return 0  # 或者根据你的需求返回一个默认值

    def generate(self, prompt, stop, on_stream=None):
        if not isinstance(prompt, str):
            raise TypeError(f"Expected string prompt, got {type(prompt)}")
        
        try:
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
            # 设置生成参数
            gen_kwargs = {
                "max_length": self.max_context_length,
                "num_return_sequences": 1,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "repetition_penalty": self.rep_pen,
                "do_sample": True,
            }

            generated_text = ""
            for output in self.model.generate(input_ids, **gen_kwargs):
                new_text = self.tokenizer.decode(output[input_ids.shape[-1]:], skip_special_tokens=True)
                generated_text += new_text
                if on_stream and callable(on_stream):
                    on_stream(new_text)
                if any(s in generated_text for s in stop):
                    break

            # 移除结尾的停止词
            for s in stop:
                if generated_text.endswith(s):
                    generated_text = generated_text[:-len(s)]
                    break

            return generated_text
        except Exception as e:
            print(f"Error in generate: {e}")
            return ""  # 或者根据你的需求返回一个默认值

    def unload(self):
        del self.model
        del self.tokenizer
        torch.cuda.empty_cache()