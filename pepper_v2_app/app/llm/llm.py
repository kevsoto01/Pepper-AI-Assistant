from ollama import chat
import subprocess
from dataclasses import dataclass 

# from ..utils.paths import OLLAMA_MODELS


@dataclass
class OllamaModelConfig:
    model: str
    num_ctx: int
    temperature: float = 0.0
    keep_alive: str = "30m"
    num_predict: int = 4
    # top_k: int = 20
    # num_ctx: int = 2048
    # num_predict: int = 80
    # repeat_penalty: float = 1.15

class OllamaLLM:
    def __init__(self, config: OllamaModelConfig):
        self.config = config
        self.options = {
            "temperature": self.config.temperature,
            "num_predict": self.config.num_predict,
            "num_ctx": self.config.num_ctx,
        }
        
    def generate_prompt(self, input_text, system_instruction, history=None) -> str:
        if history is None:
            history = []
            
        prompt = (
            [{'role': 'system', 'content': system_instruction}] 
            + history 
            + [{'role': 'user', 'content': input_text}]
            )
        
        return prompt

    def generate_response(self, prompt:list) -> str:
        response = chat(
            model = self.config.model,
            messages = prompt,
            options = self.options,
            keep_alive = self.config.keep_alive
        )
        assistant_text = response['message']['content'].strip()
        return assistant_text

    def load(self) -> None:
        prompt = self.generate_prompt("hi","")
        self.generate_response(prompt)
        
      
class ModelHub:
    def __init__(self):
        self.writer_model=None
        self.judge_model=None
        self.writer = None
        self.judge = None
        
    def apply_config(self):
        # Writer Model Config
        self.writer_temperature = 0.0#self.config_controller.get_setting("writer_llm", "temperature")
        self.writer_num_ctx = 4096#self.config_controller.get_setting("writer_llm", "max_tokens")
        
        # Judge Model Config
        self.judge_temperature = 0.0#self.config_controller.get_setting("judge_llm", "temperature")
        self.judge_num_ctx = 1024#self.config_controller.get_setting("judge_llm", "max_tokens")
        
    def load(self, writer_model:str, judge_model:str) -> None:
        self.apply_config()

        self.writer = OllamaLLM(
            OllamaModelConfig(
                model = writer_model,
                temperature = self.writer_temperature,
                keep_alive = '30m',
                num_predict = None,
                num_ctx = self.writer_num_ctx,
                )
            )
        print("Warming up writer model...")
        self.writer.load()
        
        self.judge = OllamaLLM(
            OllamaModelConfig(
                model = judge_model,
                temperature = self.judge_temperature,
                keep_alive = '30m',
                num_predict = 2,
                num_ctx = self.judge_num_ctx,
                )
            )
        print("Warming up judge model...")
        self.judge.load()
        
        print("Models ready.")
            
    def unload(self) -> None:
        print("Unloading Ollama LLMs from VRAM...")
        for model in {self.judge_model, self.writer_model}:
            if model is not None:
                subprocess.run(
                    ["ollama", "stop", model],
                    check=True
                )
        

           





