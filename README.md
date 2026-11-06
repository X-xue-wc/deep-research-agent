# Deep Research Agent 🔬

多智能体协作的深度研究系统：输入一个研究主题，自动完成「规划→搜索→反思→写作」全流程，生成结构化研究报告。

## ✨ 核心特性

- 🧠 **多智能体架构**：Planner / Searcher / Reflector / Writer 四个角色分工协作
- 🔄 **反思循环**：自动评估资料质量，不够就补充搜索（最多2轮）
- ✅ **引用校验**：自动检查所有 URL 是否真实可访问，防止幻觉
- 🗄️ **向量缓存**：Chroma 本地向量库，相似问题直接复用搜索结果
- 📕 **PDF 导出**：一键导出 Markdown / PDF 格式报告
- 🔍 **LangSmith 追踪**：完整观测 Agent 运行链路
- 🖥️ **Streamlit 界面**：可视化交互，实时显示进度

## 🏗️ 架构

```
用户输入研究主题
       ↓
  🧠 规划智能体 (Planner)
  拆解研究问题 → 生成研究大纲
       ↓
  🔍 搜索智能体 (Searcher)
  根据大纲逐条搜索 → 收集资料 → 校验URL
       ↓
  💡 反思智能体 (Reflector)
  评估资料是否充足 → 提出补充建议
       ↓  (不足则回到搜索补充，最多2轮)
  ✍️ 写作智能体 (Writer)
  基于资料撰写完整报告
       ↓
  📄 最终输出：Markdown / PDF 研究报告
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | LangGraph、LangChain |
| 模型 | DeepSeek（兼容 OpenAI 接口） |
| 搜索 | Tavily API |
| 向量库 | ChromaDB |
| 界面 | Streamlit |
| 数据校验 | Pydantic |
| 可观测 | LangSmith |

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

需要的 Key：
- **DEEPSEEK_API_KEY**：[DeepSeek 开放平台](https://platform.deepseek.com/)
- **TAVILY_API_KEY**：[Tavily](https://tavily.com/)（免费额度1000次）
- **LANGCHAIN_API_KEY**（可选）：[LangSmith](https://smith.langchain.com/)

### 3. 运行
```bash
streamlit run app.py
```

## 📁 项目结构

```
deep-research-agent/
├── agent/
│   ├── __init__.py
│   ├── state.py          # 全局状态定义（Pydantic 模型）
│   ├── llm.py            # LLM 初始化
│   ├── graph.py          # LangGraph 主图（核心编排）
│   ├── agents/
│   │   ├── planner.py    # 规划智能体
│   │   ├── searcher.py    # 搜索智能体
│   │   ├── reflector.py  # 反思智能体
│   │   └── writer.py     # 写作智能体
│   └── tools/
│       ├── search.py     # 联网搜索工具
│       ├── verify.py     # 引用校验工具
│       ├── vectorstore.py # 向量缓存
│       └── pdf_export.py # PDF 导出
├── app.py                # Streamlit 界面
├── requirements.txt       # 依赖
└── .env.example          # 环境变量模板
```

## 💼 面试讲点

1. **多智能体协作**：不是单 prompt 搞定，而是四个角色分工协作
2. **状态机编排**：用 LangGraph 管理状态流转，支持循环和条件分支
3. **反思机制**：自我评估、自我修正，这是 Agent 智能性的体现
4. **幻觉防控**：引用校验 + 来源标注，解决 LLM 编造问题
5. **工程化思维**：向量缓存、结构化输出、可观测性
6. **可扩展性**：加新智能体只要加节点和边，符合开闭原则

## 📄 License

MIT
