"""
向量库工具：用 Chroma 存储和复用搜索结果
下次类似问题直接从向量库找，不用重复搜索
"""
import os
from typing import List, Optional
import chromadb
from chromadb.utils import embedding_functions
from agent.state import SearchResult


# 全局客户端（单例）
_client = None
_collection = None


def get_vectorstore():
    """获取或创建向量库集合"""
    global _client, _collection

    if _collection is not None:
        return _collection

    # 本地持久化存储
    persist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".chroma")
    persist_dir = os.path.abspath(persist)

    _client = chromadb.PersistentClient(path=persist_dir)

    # 用默认 embedding（all-MiniLM）
    ef = embedding_functions.DefaultEmbeddingFunction()

    _collection = _client.get_or_create_collection(
        name="search_results",
        embedding_function=ef,
    )

    return _collection


def store_search_results(query: str, results: List[SearchResult]):
    """把搜索结果存到向量库"""
    collection = get_vectorstore()

    documents = []
    metadatas = []
    ids = []

    for i, r in enumerate(results):
        documents.append(f"{r.title}\n{r.content}")
        metadatas.append({
            "query": query,
            "url": r.url,
            "title": r.title,
        })
        ids.append(f"{hash(query + r.url)}_{i}")

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    print(f"  [VectorStore] 已存储 {len(results)} 条结果")


def search_vectorstore(query: str, n_results: int = 5) -> List[SearchResult]:
    """从向量库中找相似的搜索结果（命中复用）"""
    collection = get_vectorstore()

    # 先看看库里有没有数据
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, count),
    )

    search_results = []
    if results and results["documents"]:
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
            search_results.append(SearchResult(
                title=metadata.get("title", ""),
                url=metadata.get("url", ""),
                content=doc,
            ))

    if search_results:
        print(f"  [VectorStore] 命中缓存，找到 {len(search_results)} 条相似结果")

    return search_results
