#!/usr/bin/env python3
"""
使用系统Python检查虚拟环境Python的状态
"""

import os
import subprocess
import sys

# 虚拟环境Python路径
venv_python = "d:/Shado/Documents/Trae/PDF project/.venv/Scripts/python.exe"

# 检查文件是否存在
print(f"检查虚拟环境Python路径: {venv_python}")
if os.path.exists(venv_python):
    print(f"✓ 文件存在")
    
    # 检查文件权限
    if os.access(venv_python, os.X_OK):
        print(f"✓ 文件有执行权限")
    else:
        print(f"✗ 文件没有执行权限")
        
    # 尝试使用subprocess运行
    try:
        print(f"\n尝试运行虚拟环境Python...")
        result = subprocess.run([venv_python, "-c", "print('Hello from venv')"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout.strip()}")
        print(f"标准错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"运行失败: {e}")
else:
    print(f"✗ 文件不存在")

print(f"\n当前Python解释器: {sys.executable}")
print(f"当前Python版本: {sys.version}")
