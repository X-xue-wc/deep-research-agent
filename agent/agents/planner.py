"""
规划智能体：分析用户需求，拆解研究任务
这是整个系统的"大脑"
"""
import json
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

输出格式：严格的 JSON 格式，不要有任何其他文字。格式如下：
{
  "topic": "研究主题",
  "outline": "报告大纲（用换行符分隔）",
  "tasks": [
    {
      "id": 1,
      "question": "子问题1",
      "search_queries": ["关键词1", "关键词2"]
    }
  ]
}"""


def planner_node(state: AgentState) -> dict:
    """
    LangGraph 的节点函数：规划智能体
    输入：当前状态
    输出：要更新的状态字段（这里是 research_plan）
    """
    print(f"[Planner] 开始规划: {state.user_query}")

    llm = get_llm(temperature=0.2)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"研究主题：{state.user_query}"),
    ]

    response = llm.invoke(messages)
    content = response.content

    # 解析 JSON（去掉可能的 markdown 代码块标记）
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    plan_data = json.loads(content)
    plan = ResearchPlan(**plan_data)

    print(f"[Planner] 规划完成，拆解出 {len(plan.tasks)} 个任务")
    for t in plan.tasks:
        print(f"  - 任务{t.id}: {t.question}")

    return {"research_plan": plan}
