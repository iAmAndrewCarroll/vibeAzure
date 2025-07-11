"""
LLM Handler with multiple backend support
"""
import subprocess
import json
from typing import Optional

class LLMHandler:
    def __init__(self, backend="ollama", model_name="tinyllama"):
        self.backend = backend
        self.model_name = model_name
        self.llm = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the chosen LLM backend"""
        if self.backend == "ollama":
            self._test_ollama_connection()
        elif self.backend == "llama-cpp":
            self._initialize_llama_cpp()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _test_ollama_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                raise Exception("Ollama not running")
            
            # Check if our model is available
            if self.model_name not in result.stdout:
                print(f"[yellow]Model {self.model_name} not found. Pulling it...[/yellow]")
                subprocess.run(["ollama", "pull", self.model_name], check=True)
                
        except Exception as e:
            print(f"[red]Ollama setup failed: {e}[/red]")
            print("[yellow]Install Ollama from https://ollama.com[/yellow]")
            raise
    
    def _initialize_llama_cpp(self):
        """Initialize llama-cpp-python backend"""
        try:
            from llama_cpp import Llama
            MODEL_PATH = "models/tinyllama.gguf"
            self.llm = Llama(model_path=MODEL_PATH, n_ctx=512, verbose=False)
        except ImportError:
            print("[red]llama-cpp-python not installed. Run: pip install llama-cpp-python[/red]")
            raise
        except Exception as e:
            print(f"[red]Failed to load model: {e}[/red]")
            raise
    
    def ask(self, prompt: str) -> str:
        """Ask the LLM a question"""
        try:
            if self.backend == "ollama":
                return self._ask_ollama(prompt)
            elif self.backend == "llama-cpp":
                return self._ask_llama_cpp(prompt)
        except Exception as e:
            return f"Error getting AI response: {e}"
    
    def _ask_ollama(self, prompt: str) -> str:
        """Query Ollama"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        result = subprocess.run(
            ["ollama", "generate", "--format", "json"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Ollama error: {result.stderr}"
        
        try:
            response_data = json.loads(result.stdout)
            return response_data.get("response", "No response received").strip()
        except json.JSONDecodeError:
            return result.stdout.strip()
    
    def _ask_llama_cpp(self, prompt: str) -> str:
        """Query llama-cpp-python"""
        response = self.llm(prompt, max_tokens=300)
        return response['choices'][0]['text'].strip()
