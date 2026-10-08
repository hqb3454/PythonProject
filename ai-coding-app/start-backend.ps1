Set-Location F:\PythonProject\ai-coding-app\backend
$env:RAG_MCP_URL = if ($env:RAG_MCP_URL) { $env:RAG_MCP_URL } else { "http://127.0.0.1:8766/mcp" }
F:\PythonProject\rag\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
