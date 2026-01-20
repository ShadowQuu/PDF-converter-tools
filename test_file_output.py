#!/usr/bin/env python3
"""
将输出写入文件的测试脚本
"""

import sys
import os

# 输出到文件
output_file = "test_output.txt"
with open(output_file, "w") as f:
    f.write("=== 测试脚本输出 ===\n")
    f.write(f"Python版本: {sys.version}\n")
    f.write(f"Python路径: {sys.executable}\n")
    f.write(f"当前工作目录: {os.getcwd()}\n")
    f.write(f"脚本路径: {os.path.abspath(__file__)}\n")
    
    # 测试PyQt6导入
    try:
        f.write("\n=== 测试PyQt6导入 ===\n")
        from PyQt6.QtWidgets import QApplication
        f.write("✓ 成功导入QApplication\n")
        
        from PyQt6.QtWidgets import QMainWindow
        f.write("✓ 成功导入QMainWindow\n")
        
        from PyQt6.QtGui import QIcon, QPixmap, QAction
        f.write("✓ 成功导入QtGui模块\n")
        
        from PyQt6.QtCore import Qt, QUrl
        f.write("✓ 成功导入QtCore模块\n")
        
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        f.write("✓ 成功导入QWebEngineView\n")
        
        f.write("\n✓ 所有PyQt6模块导入成功\n")
    except Exception as e:
        f.write(f"✗ 导入PyQt6模块失败: {e}\n")
    
    # 测试其他依赖
    try:
        f.write("\n=== 测试其他依赖 ===\n")
        import pdfkit
        f.write("✓ 成功导入pdfkit\n")
        
        from PIL import Image
        f.write("✓ 成功导入PIL.Image\n")
        
        from PyPDF2 import PdfReader, PdfWriter
        f.write("✓ 成功导入PyPDF2\n")
        
        import pikepdf
        f.write("✓ 成功导入pikepdf\n")
        
        from reportlab.lib.pagesizes import A4, landscape
        f.write("✓ 成功导入reportlab\n")
        
        from executable_detector import detect_executable
        f.write("✓ 成功导入executable_detector\n")
        
        f.write("\n✓ 所有依赖导入成功\n")
    except Exception as e:
        f.write(f"✗ 导入其他依赖失败: {e}\n")
    
    f.write("\n=== 测试脚本执行完毕 ===\n")

# 也打印到终端，以便确认脚本执行
print(f"测试输出已写入到文件: {output_file}")
