"""
搜索工具：给智能体用的联网搜索能力
基于 Tavily API，专门为 LLM 优化的搜索服务
"""
import os
from typing import List
from tavily import TavilyClient
from agent.state import SearchResult


def get_tavily_client() -> TavilyClient:
    """获取 Tavily 客户端"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("请先设置 TAVILY_API_KEY 环境变量")
    return TavilyClient(api_key=api_key)


def search_web(query: str, max_results: int = 5) -> List[SearchResult]:
    """
    联网搜索工具
    :param query: 搜索关键词
    :param max_results: 最多返回几条结果
    :return: 结构化的搜索结果列表
    """
    client = get_tavily_client()

    # 调用 Tavily 搜索
    response = client.search(
        query=query,
        search_depth="advanced",  # 深度搜索，质量更高
        max_results=max_results,
        include_answer=True,  # 让它生成一个总结答案
    )

    # 把结果转成我们定义的 SearchResult 结构
    results = []
    for item in response.get("results", []):
        results.append(SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            content=item.get("content", ""),
        ))

    return results


def search_with_context(query: str) -> str:
    """
    带上下文的搜索：直接返回拼接好的文本，方便塞给 LLM
    """
    results = search_web(query)

    if not results:
        return "未搜索到相关结果"

    # 拼接成 LLM 能直接读的格式
    text_parts = []
    for i, r in enumerate(results, 1):
        text_parts.append(f"[{i}] {r.title}\n{r.content}\n来源: {r.url}")

    return "\n\n".join(text_parts)
