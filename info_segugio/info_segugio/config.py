import os

### LLM in Locale
class Config:
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")  # "deepseek-r1:1.5b" # "llama3.2" # "deepseek-r1:1.5b"
    LLM_MODEL_LOW = os.getenv("LLM_MODEL_LOW", "deepseek-r1:1.5b")  # "deepseek-r1:1.5b" # "llama3.2" # "deepseek-r1:1.5b"
    AI_API_URL = os.getenv("AI_API_URL", "http://localhost:11434/v1")
    AI_API_KEY = os.getenv("AI_API_KEY", "ollama")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "tvly-YOUR_API_KEY")

### LLM su OpenAI
# class Config:
#     LLM_MODEL = "gpt-4o"
#     LLM_MODEL_LOW = "gpt-4o-mini"
#     AI_API_URL = "https://api.openai.com/v1"
#     AI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
