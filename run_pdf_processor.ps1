#!/usr/bin/env powershell
# PDF处理器运行脚本

# 直接使用完整路径运行
Write-Host "正在运行PDF处理器..." -ForegroundColor Green
& 'd:\Shado\Documents\Trae\PDF project\.venv\Scripts\python.exe' pdf_processor_cli.py $args
