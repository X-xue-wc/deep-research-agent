@echo off
cd /d D:\deep-research-agent
echo ========================================
echo   Deep Research Agent 启动中...
echo   浏览器打开: http://localhost:8501
echo   按 Ctrl+C 停止
echo ========================================
echo.
streamlit run app.py
pause
