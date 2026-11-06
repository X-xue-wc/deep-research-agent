"""
测试脚本：直接运行 Agent，查看每一步状态
"""
from agent.graph import agent_app
from agent.state import AgentState

print("Starting agent...")
initial_state = AgentState(user_query="2025年AI Agent行业发展趋势")

# 运行，打印每一步
for event in agent_app.stream(initial_state, stream_mode="values"):
    state = event
    rp = state.get("research_plan")
    refl = state.get("reflection")
    idx = state.get("current_task_idx", 0)
    final = state.get("final_report")
    rnd = state.get("reflection_round", 0)

    if rp is None:
        print("Step: Planning...")
    elif refl is None:
        if isinstance(rp, dict):
            tasks = rp.get("tasks", [])
        else:
            tasks = getattr(rp, "tasks", [])
        print(f"Step: Searching... {idx}/{len(tasks)} tasks")
    elif final is None:
        print(f"Step: Reflecting/Writing... round={rnd}")
    else:
        print("Step: Done!")
        print(f"Report length: {len(final)} chars")
        print("--- First 500 chars ---")
        print(final[:500])
        break
