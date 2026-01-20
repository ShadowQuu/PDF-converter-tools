#!/usr/bin/env python3
"""
极简测试脚本，只打印基本信息
"""

import sys
import os

print("=== 极简测试脚本 ===")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本路径: {os.path.abspath(__file__)}")
print("=== 测试脚本执行完毕 ===")
