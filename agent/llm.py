"""
LLM 初始化：统一管理大模型调用
用 DeepSeek，兼容 OpenAI 接口格式
"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    """
    获取 LLM 实例
    :param temperature: 温度系数，越低越稳定（规划/搜索用低温度，写作用稍高）
    """
    return ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        temperature=temperature,
        timeout=60,
    )
