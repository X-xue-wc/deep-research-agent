"""
LLM 初始化：统一管理大模型调用
用 DeepSeek，兼容 OpenAI 接口格式
"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 强制加载 .env 文件，覆盖已有的环境变量
load_dotenv(override=True)


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    """
    获取 LLM 实例
    :param temperature: 温度系数，越低越稳定（规划/搜索用低温度，写作用稍高）
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    print(f"[LLM] 使用模型: {model}, Key 最后4位: ...{api_key[-4:] if api_key else 'None'}")

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        timeout=60,
    )
