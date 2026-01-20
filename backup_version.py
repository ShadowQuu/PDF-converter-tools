import datetime
import os
import zipfile

# 设置版本号
version = '1.0.1'

timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
zip_name = f'pdf_tool_v{version}_{timestamp}.zip'

# 创建备份文件
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        for file in files:
            # 备份Python源文件、文本文件和Markdown文件
            if file.endswith(('.py', '.txt', '.md')):
                # 跳过虚拟环境和缓存文件夹
                if not (root.startswith('./.venv') or root.startswith('./__pycache__')):
                    # 构建相对路径
                    file_path = os.path.join(root, file)
                    zipf.write(file_path)

print(f'已创建版本备份: {zip_name}')
print(f'版本号: {version}')
print(f'备份时间: {timestamp}')
