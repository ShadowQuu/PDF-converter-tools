#!/usr/bin/env python3
"""
简单的测试脚本，用于诊断PIL/Pillow模块问题
"""
import sys
import os

print("Python版本:", sys.version)
print("Python可执行文件路径:", sys.executable)
print("当前工作目录:", os.getcwd())

# 尝试导入PIL模块
print("\n=== 测试PIL/Pillow导入 ===")
try:
    from PIL import Image
    print("✓ 成功导入PIL模块")
    print("Pillow版本:", Image.__version__)
    print("Image模块路径:", Image.__file__)
except ImportError as e:
    print("✗ 导入PIL模块失败:", e)
    print("\n=== 系统路径检查 ===")
    print("sys.path:")
    for path in sys.path:
        print(f"  - {path}")
    
    print("\n=== 检查Pillow安装 ===")
    try:
        import pkg_resources
        installed_packages = pkg_resources.working_set
        pillow_packages = [pkg for pkg in installed_packages if "pillow" in pkg.key.lower()]
        if pillow_packages:
            print("已安装的Pillow包:")
            for pkg in pillow_packages:
                print(f"  - {pkg.key} {pkg.version}")
        else:
            print("未找到已安装的Pillow包")
    except Exception as e:
        print("检查Pillow安装失败:", e)

# 测试其他依赖
print("\n=== 测试其他依赖 ===")
dependencies = ["PyPDF2", "pdfkit", "pikepdf", "reportlab"]
for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ 成功导入{dep}")
    except ImportError as e:
        print(f"✗ 导入{dep}失败:", e)
