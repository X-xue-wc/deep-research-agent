"""
搜索智能体：执行具体的搜索任务，收集资料
升级：加引用校验 + 向量库复用
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agent.llm import get_llm
from agent.state import AgentState, TaskResult, ResearchTask, SearchResult
from agent.tools.search import search_web
from agent.tools.verify import verify_sources
from agent.tools.vectorstore import search_vectorstore, store_search_results


SEARCHER_SYSTEM_PROMPT = """你是一个研究助理。给定一个研究问题和搜索结果，
请总结核心发现，提炼关键信息。

要求：
1. 基于搜索结果总结，不要编造
2. 重点突出有价值的发现
3. 简洁明了，控制在 300 字以内
4. 标注信息来源的可靠性"""


def searcher_node(state: AgentState) -> dict:
    """
    LangGraph 节点：搜索智能体
    支持两种模式：
    1. 正常任务循环
    2. 反思后的补充搜索
    """
    # 情况1：正常的任务循环
    if state.reflection is None:
        return _normal_search(state)
    # 情况2：反思后的补充搜索
    else:
        return _followup_search(state)


def _normal_search(state: AgentState) -> dict:
    """正常模式：按规划的任务列表逐个搜索"""
    plan = state.research_plan
    current_idx = state.current_task_idx

    if current_idx >= len(plan.tasks):
        print(f"[Searcher] 所有 {len(plan.tasks)} 个任务已完成")
        return {}

    task: ResearchTask = plan.tasks[current_idx]
    print(f"[Searcher] 执行任务 {task.id}: {task.question}")

    all_sources = []
    all_findings = []

    for query in task.search_queries:
        print(f"  搜索: {query}")

        # 先查向量库有没有缓存
        cached = search_vectorstore(query)
        if cached:
            all_sources.extend(cached)
        else:
            results = search_web(query, max_results=3)
            # 校验 URL
            verified = verify_sources(results)
            all_sources.extend(verified)
            # 存入向量库
            store_search_results(query, verified)

        # 总结搜索结果
        results_text = "\n".join([
            f"标题: {r.title}\n内容: {r.content}"
            for r in all_sources[-3:]
        ])

        llm = get_llm(temperature=0.1)
        response = llm.invoke([
            SystemMessage(content=SEARCHER_SYSTEM_PROMPT),
            HumanMessage(content=f"研究问题: {task.question}\n\n搜索结果:\n{results_text}"),
        ])
        all_findings.append(response.content)

    task_result = TaskResult(
        task_id=task.id,
        question=task.question,
        findings="\n".join(all_findings),
        sources=all_sources[:5],
    )

    print(f"  完成，收集到 {len(all_sources)} 个来源")

    return {
        "task_results": state.task_results + [task_result],
        "current_task_idx": current_idx + 1,
    }


def _followup_search(state: AgentState) -> dict:
    """补充搜索模式：根据反思建议补充搜索"""
    suggestions = state.reflection.suggestions
    if not suggestions:
        return {}

    print(f"[Searcher] 补充搜索 {len(suggestions)} 个问题...")

    for i, query in enumerate(suggestions):
        print(f"  补充搜索: {query}")
        results = search_web(query, max_results=3)
        verified = verify_sources(results)
        store_search_results(query, verified)

        # 总结
        results_text = "\n".join([
            f"标题: {r.title}\n内容: {r.content}"
            for r in verified
        ])

        llm = get_llm(temperature=0.1)
        response = llm.invoke([
            SystemMessage(content=SEARCHER_SYSTEM_PROMPT),
            HumanMessage(content=f"补充研究问题: {query}\n\n搜索结果:\n{results_text}"),
        ])

        # 加到任务结果里
        new_task = TaskResult(
            task_id=100 + i,  # 100+ 编号表示补充任务
            question=query,
            findings=response.content,
            sources=verified,
        )

    print(f"[Searcher] 补充搜索完成")

    return {
        "task_results": state.task_results + [new_task],
    }


def should_continue_searching(state: AgentState) -> str:
    """
    条件判断：决定是继续搜索下一个任务，还是去反思
    """
    # 还没开始反思过
    if state.reflection is None:
        if state.current_task_idx < len(state.research_plan.tasks):
            return "continue"
        return "reflect"  # 所有任务做完了，去反思

    # 已经反思过了，补充搜索完了，回去再反思
    return "reflect"
