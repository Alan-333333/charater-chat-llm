import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from backend import backend
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class backend_llama3(backend):
    def __init__(self, model_directory, max_context_length=2048):
        super().__init__()
        self.max_context_length = max_context_length
        
        logger.info(f"Loading tokenizer from {model_directory}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_directory)
        
        # Set pad_token to a unique token
        self.tokenizer.pad_token = '[PAD]'
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        logger.info(f"Set pad_token to: {self.tokenizer.pad_token}")
        
        logger.info(f"Loading model from {model_directory}")
        self._model = AutoModelForCausalLM.from_pretrained(
            model_directory,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        )
        
        # Resize token embeddings to account for new pad token
        self._model.resize_token_embeddings(len(self.tokenizer))
        
        # Update model config
        self._model.config.pad_token_id = self.tokenizer.pad_token_id
        logger.info(f"Model loaded. pad_token_id: {self._model.config.pad_token_id}")
        
        self._model.eval()

    def tokens_count(self, text):
        return len(self.tokenizer.encode(text))

    def generate(self, prompt, stop, on_stream=None):
        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=self.max_context_length)
        input_ids = inputs["input_ids"].to(self._model.device)
        attention_mask = inputs["attention_mask"].to(self._model.device)
        
        gen_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_length": self.max_context_length,
            "do_sample": True,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.rep_pen,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        def generate():
            with torch.no_grad():
                output = self._model.generate(**gen_kwargs)
                generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
                logger.info(f"Generated text: {generated_text[:50]}...")
                return generated_text[len(prompt):]  # Remove the input prompt from the output

        result = self.process(generate, stop, on_stream)
        return result

    def unload(self):
        if self._model is None:
            return

        logger.info("Unloading model and freeing up resources")
        del self._model
        self._model = None
        self.tokenizer = None

        import gc
        gc.collect()
        torch.cuda.empty_cache()