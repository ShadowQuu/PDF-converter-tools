#!/usr/bin/env python3
"""
捕获命令输出并写入文件
"""

import os
import subprocess

# 要执行的命令
commands = [
    "dir",
    "python --version",
    "python -c \"print('Hello from system Python')\"",
    ".venv/Scripts/python.exe --version",
    ".venv/Scripts/python.exe -c \"print('Hello from venv Python')\""
]

# 输出到文件
output_file = "command_outputs.txt"
with open(output_file, "w") as f:
    for cmd in commands:
        f.write(f"\n=== 执行命令: {cmd} ===\n")
        try:
            # 使用subprocess捕获输出
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            f.write(f"返回码: {result.returncode}\n")
            f.write(f"标准输出:\n{result.stdout}\n")
            f.write(f"标准错误:\n{result.stderr}\n")
        except Exception as e:
            f.write(f"执行失败: {e}\n")

print(f"所有命令输出已写入到文件: {output_file}")
