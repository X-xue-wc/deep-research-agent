"""
状态定义：整个 Agent 系统的共享数据结构
用 Pydantic 做类型校验，确保每个智能体输出的数据格式正确
"""
from typing import List, Optional, Dict, Any
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing import Annotated
from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    """单个研究子任务（规划智能体拆解出来的）"""
    id: int = Field(description="任务编号")
    question: str = Field(description="具体要研究的问题")
    search_queries: List[str] = Field(description="搜索关键词列表")


class ResearchPlan(BaseModel):
    """研究计划：规划智能体的输出"""
    topic: str = Field(description="研究主题")
    outline: str = Field(description="报告大纲")
    tasks: List[ResearchTask] = Field(description="拆解后的研究任务列表")


class SearchResult(BaseModel):
    """单个搜索结果"""
    title: str = Field(description="搜索结果标题")
    url: str = Field(description="来源链接")
    content: str = Field(description="摘要内容")
    is_valid: bool = Field(default=True, description="引用是否经过校验")


class TaskResult(BaseModel):
    """单个研究任务的执行结果"""
    task_id: int = Field(description="对应任务编号")
    question: str = Field(description="研究的问题")
    findings: str = Field(description="研究发现")
    sources: List[SearchResult] = Field(description="参考来源")
    is_sufficient: bool = Field(default=True, description="资料是否充足")
    follow_up_questions: List[str] = Field(default_factory=list, description="需要补充搜索的问题")


class ReflectionResult(BaseModel):
    """反思智能体的输出"""
    overall_sufficient: bool = Field(description="整体资料是否充足")
    gaps: List[str] = Field(default_factory=list, description="发现的知识缺口")
    suggestions: List[str] = Field(default_factory=list, description="补充搜索建议")


class AgentState(BaseModel):
    """
    全局状态：在 LangGraph 各个节点之间流转
    这是整个系统的"共享内存"
    """
    # 用户原始输入
    user_query: str = Field(description="用户的研究需求")

    # 规划阶段
    research_plan: Optional[ResearchPlan] = Field(
        default=None, description="研究计划（规划智能体输出）"
    )

    # 搜索阶段
    current_task_idx: int = Field(default=0, description="当前执行到第几个任务")
    task_results: List[TaskResult] = Field(default_factory=list, description="已完成的任务结果")

    # 反思阶段
    reflection: Optional[ReflectionResult] = Field(default=None, description="反思结果")
    reflection_round: int = Field(default=0, description="反思轮次（最多2轮）")

    # 写作阶段
    final_report: Optional[str] = Field(default=None, description="最终研究报告")

    # 消息历史（用于 LLM 对话上下文）
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
