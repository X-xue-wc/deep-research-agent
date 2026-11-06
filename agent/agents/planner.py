"""
规划智能体：分析用户需求，拆解研究任务
这是整个系统的"大脑"
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agent.llm import get_llm
from agent.state import AgentState, ResearchPlan


# 规划智能体的 System Prompt
PLANNER_SYSTEM_PROMPT = """你是一个专业的研究规划专家。你的任务是：

1. 理解用户的研究主题和需求
2. 把大问题拆解成 3-5 个具体的、可搜索的子问题
3. 为每个子问题生成 2-3 个精准的搜索关键词
4. 设计一个报告大纲

要求：
- 子问题要相互独立，合起来又能覆盖完整主题
- 搜索关键词要具体，不要太泛
- 大纲要有逻辑层次，符合学术报告规范
- 输出必须符合给定的 JSON 格式"""


def planner_node(state: AgentState) -> dict:
    """
    LangGraph 的节点函数：规划智能体
    输入：当前状态
    输出：要更新的状态字段（这里是 research_plan）
    """
    print(f"[Planner] 开始规划: {state.user_query}")

    llm = get_llm(temperature=0.2)

    # 让 LLM 直接输出结构化的 ResearchPlan 对象
    structured_llm = llm.with_structured_output(ResearchPlan)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"研究主题：{state.user_query}"),
    ]

    plan = structured_llm.invoke(messages)

    print(f"[Planner] 规划完成，拆解出 {len(plan.tasks)} 个任务")
    for t in plan.tasks:
        print(f"  - 任务{t.id}: {t.question}")

    return {"research_plan": plan}
