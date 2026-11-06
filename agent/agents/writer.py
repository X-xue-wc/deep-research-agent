"""
写作智能体：把所有研究发现整合成完整报告
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agent.llm import get_llm
from agent.state import AgentState


WRITER_SYSTEM_PROMPT = """你是一个专业的研究报告撰写专家。

请根据以下材料撰写一份完整的研究报告：
1. 按照给定的大纲结构组织内容
2. 把各部分的研究发现有机地整合起来，不要只是罗列
3. 每个关键论断都要标注参考来源
4. 语言专业、逻辑清晰
5. 最后加一个总结和参考来源列表

输出格式：Markdown 格式"""


def writer_node(state: AgentState) -> dict:
    """LangGraph 节点：写作智能体"""
    print(f"[Writer] 开始撰写最终报告...")

    plan = state.research_plan
    task_results = state.task_results

    # 把所有研究发现拼成材料
    materials = []
    for tr in task_results:
        sources_text = "\n".join([
            f"[{i+1}] {s.title} ({s.url})"
            for i, s in enumerate(tr.sources)
        ])
        materials.append(
            f"## 问题：{tr.question}\n\n"
            f"研究发现：\n{tr.findings}\n\n"
            f"参考来源：\n{sources_text}"
        )

    materials_text = "\n\n".join(materials)

    llm = get_llm(temperature=0.5)  # 写作用稍高温度，语言更自然

    response = llm.invoke([
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"研究主题：{plan.topic}\n\n"
            f"报告大纲：\n{plan.outline}\n\n"
            f"研究材料：\n{materials_text}"
        )),
    ])

    print(f"[Writer] 报告完成，共 {len(response.content)} 字")

    return {"final_report": response.content}
