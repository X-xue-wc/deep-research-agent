"""
反思智能体：评估搜索结果是否充足，提出补充搜索建议
这是提升研究质量的关键环节
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agent.llm import get_llm
from agent.state import AgentState, ReflectionResult


REFLECT_SYSTEM_PROMPT = """你是一个研究质量评审专家。

请评估当前的研究材料是否足够支撑一份高质量的研究报告。

评估维度：
1. 覆盖度：是否覆盖了所有关键方面？
2. 时效性：信息是否最新？
3. 深度：是否有足够的细节和数据支撑？
4. 平衡性：是否有不同角度的观点？

输出要求：
- 如果材料基本充足，overall_sufficient = true
- 如果有明显缺口，列出 gaps 和需要补充搜索的 suggestions
- 最多提出 3 个补充搜索建议，不要太多"""


def reflect_node(state: AgentState) -> dict:
    """LangGraph 节点：反思智能体"""
    print(f"[Reflector] 第 {state.reflection_round + 1} 轮反思...")

    # 把所有任务结果拼成材料
    materials = []
    for tr in state.task_results:
        materials.append(f"问题：{tr.question}\n发现：{tr.findings}\n")

    materials_text = "\n\n".join(materials)

    llm = get_llm(temperature=0.2)
    structured_llm = llm.with_structured_output(ReflectionResult)

    messages = [
        SystemMessage(content=REFLECT_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"研究主题：{state.research_plan.topic}\n\n"
            f"研究材料：\n{materials_text}\n\n"
            f"请评估材料是否充足，并给出补充建议。"
        )),
    ]

    reflection = structured_llm.invoke(messages)

    if reflection.overall_sufficient:
        print(f"[Reflector] 材料充足，可以写作")
    else:
        print(f"[Reflector] 发现 {len(reflection.gaps)} 个缺口，建议补充 {len(reflection.suggestions)} 个搜索")
        for s in reflection.suggestions:
            print(f"  - {s}")

    return {
        "reflection": reflection,
        "reflection_round": state.reflection_round + 1,
    }


def should_reflect_again(state: AgentState) -> str:
    """
    条件判断：反思完了之后怎么办
    - 如果材料不足且没超过2轮 → 回去补充搜索
    - 否则 → 去写作
    """
    # 已经反思过了，材料还是不足，但不超过2轮
    if not state.reflection.overall_sufficient and state.reflection_round < 2:
        return "search_more"  # 回去补充搜索

    return "write"  # 去写作
