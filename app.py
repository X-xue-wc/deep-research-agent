"""
Streamlit 界面：和 Agent 对话的窗口
升级：显示反思进度 + PDF 导出
"""
import streamlit as st
from agent.graph import agent_app
from agent.state import AgentState
from agent.tools.pdf_export import markdown_to_pdf
import tempfile
import os

st.set_page_config(page_title="Deep Research Agent", page_icon="🔬", layout="wide")

st.title("🔬 Deep Research Agent")
st.caption("多智能体协作的深度研究系统 | 规划→搜索→反思→写作 全自动")

# 侧边栏
with st.sidebar:
    st.header("工作流程")
    st.markdown("""
    1. 🧠 **Planner** 拆解研究问题
    2. 🔍 **Searcher** 逐条搜索资料
    3. 💡 **Reflector** 反思评估质量
    4. ✍️ **Writer** 撰写完整报告
    """)
    st.divider()
    st.markdown("💡 试试输入：")
    st.markdown("- 2025年AI Agent行业发展趋势")
    st.markdown("- 对比LangChain和LangGraph的区别")
    st.markdown("- 应届生秋招AI应用开发岗位攻略")

# 主界面
user_query = st.text_area("📝 输入你的研究主题", height=100,
                          placeholder="例如：2025年AI Agent技术发展趋势和就业前景分析")

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🚀 开始研究", type="primary", use_container_width=True)

if run_button and user_query:
    initial_state = AgentState(user_query=user_query)

    progress_placeholder = st.empty()
    report_placeholder = st.empty()

    for event in agent_app.stream(initial_state, stream_mode="values"):
        state: AgentState = event

        # 实时更新进度
        if state.research_plan is None:
            progress_placeholder.info("🧠 规划智能体正在分析研究主题...")

        elif state.reflection is None:
            if state.current_task_idx < len(state.research_plan.tasks):
                progress_placeholder.info(
                    f"🔍 搜索智能体正在研究... "
                    f"({state.current_task_idx}/{len(state.research_plan.tasks)} 个任务)"
                )
            else:
                progress_placeholder.info("🔍 搜索完成，准备反思...")

        elif state.final_report is None:
            if not state.reflection.overall_sufficient:
                progress_placeholder.info(
                    f"💡 反思智能体发现缺口，正在补充搜索... "
                    f"(第 {state.reflection_round} 轮)"
                )
            else:
                progress_placeholder.info("✍️ 写作智能体正在撰写报告...")

        else:
            progress_placeholder.success("✅ 研究完成！")
            report_placeholder.markdown(state.final_report)

            # 下载按钮区
            st.divider()
            st.subheader("📥 导出报告")

            col_md, col_pdf = st.columns(2)

            with col_md:
                st.download_button(
                    label="📄 下载 Markdown",
                    data=state.final_report,
                    file_name="research_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            with col_pdf:
                # 生成 PDF
                try:
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        pdf_path = tmp.name
                    markdown_to_pdf(state.final_report, pdf_path)
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="📕 下载 PDF",
                        data=pdf_bytes,
                        file_name="research_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    os.unlink(pdf_path)
                except Exception as e:
                    st.error(f"PDF 生成失败：{e}")

elif run_button and not user_query:
    st.warning("请先输入研究主题")
