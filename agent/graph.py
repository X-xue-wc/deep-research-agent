"""
主图：把所有智能体组装成完整的工作流
流程：规划 → 搜索（循环） → 反思 → 补充搜索 → 写作
"""
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.agents.planner import planner_node
from agent.agents.searcher import searcher_node, should_continue_searching
from agent.agents.reflector import reflect_node, should_reflect_again
from agent.agents.writer import writer_node


def build_agent():
    """
    构建完整的 Agent 工作流
    """
    # 1. 创建状态图
    workflow = StateGraph(AgentState)

    # 2. 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("searcher", searcher_node)
    workflow.add_node("reflector", reflect_node)
    workflow.add_node("writer", writer_node)

    # 3. 入口点：从规划开始
    workflow.set_entry_point("planner")

    # 4. 添加边
    # 规划完 → 去搜索
    workflow.add_edge("planner", "searcher")

    # 搜索完 → 条件判断
    workflow.add_conditional_edges(
        "searcher",
        should_continue_searching,
        {
            "continue": "searcher",  # 还有任务，继续搜索
            "reflect": "reflector",  # 任务做完了，去反思
        }
    )

    # 反思完 → 条件判断
    workflow.add_conditional_edges(
        "reflector",
        should_reflect_again,
        {
            "search_more": "searcher",  # 材料不够，补充搜索
            "write": "writer",           # 材料够了，去写作
        }
    )

    # 写作完 → 结束
    workflow.add_edge("writer", END)

    # 5. 编译
    app = workflow.compile()

    return app


# 预编译
agent_app = build_agent()
