#!/usr/bin/env python3
"""
简单测试脚本，用于调试程序运行问题
"""

import sys
import os

print("=== 简单测试脚本 ===")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本路径: {os.path.abspath(__file__)}")

# 测试PyQt6导入
try:
    print("\n=== 测试PyQt6导入 ===")
    from PyQt6.QtWidgets import QApplication
    print("✓ 成功导入QApplication")
    
    from PyQt6.QtWidgets import QMainWindow
    print("✓ 成功导入QMainWindow")
    
    from PyQt6.QtGui import QIcon, QPixmap, QAction
    print("✓ 成功导入QtGui模块")
    
    from PyQt6.QtCore import Qt, QUrl
    print("✓ 成功导入QtCore模块")
    
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("✓ 成功导入QWebEngineView")
    
    print("\n✓ 所有PyQt6模块导入成功")
except Exception as e:
    print(f"✗ 导入PyQt6模块失败: {e}")

# 测试其他依赖
try:
    print("\n=== 测试其他依赖 ===")
    import pdfkit
    print("✓ 成功导入pdfkit")
    
    from PIL import Image
    print("✓ 成功导入PIL.Image")
    
    from PyPDF2 import PdfReader, PdfWriter
    print("✓ 成功导入PyPDF2")
    
    import pikepdf
    print("✓ 成功导入pikepdf")
    
    from reportlab.lib.pagesizes import A4, landscape
    print("✓ 成功导入reportlab")
    
    from executable_detector import detect_executable
    print("✓ 成功导入executable_detector")
    
    print("\n✓ 所有依赖导入成功")
except Exception as e:
    print(f"✗ 导入其他依赖失败: {e}")

print("\n=== 测试脚本执行完毕 ===")
