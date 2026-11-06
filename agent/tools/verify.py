"""
引用校验工具：检查 URL 是否真实可访问
防止幻觉引用
"""
import requests
from typing import List
from agent.state import SearchResult


def verify_url(url: str, timeout: int = 5) -> bool:
    """
    检查 URL 是否可以正常访问
    返回 True/False
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        # 2xx 和 3xx 都算有效
        return resp.status_code < 400
    except requests.RequestException:
        try:
            # 有些网站 HEAD 不支持，试试 GET
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            return resp.status_code < 400
        except requests.RequestException:
            return False


def verify_sources(sources: List[SearchResult]) -> List[SearchResult]:
    """
    批量校验搜索结果的 URL
    """
    verified = []
    for s in sources:
        is_valid = verify_url(s.url)
        verified.append(SearchResult(
            title=s.title,
            url=s.url,
            content=s.content,
            is_valid=is_valid,
        ))
        status = "✓" if is_valid else "✗"
        print(f"  [{status}] {s.url}")

    return verified
