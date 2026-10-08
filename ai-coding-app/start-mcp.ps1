Set-Location F:\PythonProject\mcp-rag
$port = if ($args.Count -gt 0) { $args[0] } else { "8766" }
F:\PythonProject\rag\.venv\Scripts\python.exe http_server.py $port
