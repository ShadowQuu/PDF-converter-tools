#!/usr/bin/env python3
"""
可执行文件自动检测模块

该模块提供了一个通用的可执行文件检测机制，用于自动检测和验证外部依赖。
"""

import os
import sys
import subprocess
import json
import platform
from typing import Optional, Dict, List

class ExecutableDetector:
    """
    可执行文件自动检测器
    """
    
    def __init__(self, config_file: str = 'executable_paths.json'):
        """
        初始化检测器
        
        Args:
            config_file: 配置文件路径，用于存储检测到的可执行文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, str]:
        """
        加载配置文件
        
        Returns:
            配置字典，包含已检测到的可执行文件路径
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_config(self) -> None:
        """
        保存配置文件
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            # 保存失败不影响程序运行，只记录日志
            pass
    
    def _get_platform_paths(self) -> List[str]:
        """
        获取当前平台的常见可执行文件路径
        
        Returns:
            常见可执行文件路径列表
        """
        paths = []
        
        # 获取系统PATH环境变量
        if 'PATH' in os.environ:
            paths.extend(os.environ['PATH'].split(os.pathsep))
        
        # 添加平台特定的常见路径
        system = platform.system()
        
        if system == 'Windows':
            # Windows特定路径
            paths.extend([
                r'C:\Program Files\wkhtmltopdf\bin',
                r'C:\Program Files (x86)\wkhtmltopdf\bin',
                r'C:\Program Files\wkhtmltopdf',
                r'C:\Program Files (x86)\wkhtmltopdf',
                os.path.expanduser(r'~\AppData\Local\Programs\wkhtmltopdf'),
                os.path.expanduser(r'~\AppData\Roaming\wkhtmltopdf'),
            ])
        elif system == 'Darwin':  # macOS
            # macOS特定路径
            paths.extend([
                '/usr/local/bin',
                '/usr/bin',
                '/opt/homebrew/bin',
                '/opt/local/bin',
                os.path.expanduser('~/bin'),
            ])
        else:  # Linux
            # Linux特定路径
            paths.extend([
                '/usr/local/bin',
                '/usr/bin',
                '/bin',
                '/snap/bin',
                os.path.expanduser('~/bin'),
            ])
        
        return paths
    
    def _get_executable_name(self, base_name: str) -> str:
        """
        获取带扩展名的可执行文件名
        
        Args:
            base_name: 可执行文件基础名称
            
        Returns:
            带扩展名的可执行文件名
        """
        if platform.system() == 'Windows' and not base_name.endswith('.exe'):
            return f'{base_name}.exe'
        return base_name
    
    def _check_executable_version(self, executable_path: str, version_flags: List[str] = ['--version']) -> bool:
        """
        检查可执行文件版本是否兼容
        
        Args:
            executable_path: 可执行文件路径
            version_flags: 用于获取版本的命令行参数
            
        Returns:
            版本兼容返回True，否则返回False
        """
        try:
            result = subprocess.run(
                [executable_path] + version_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            # 只要命令成功执行，就认为版本兼容
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False
    
    def detect(self, executable_name: str, version_flags: List[str] = ['--version'], force: bool = False) -> Optional[str]:
        """
        自动检测可执行文件路径
        
        Args:
            executable_name: 可执行文件名称
            version_flags: 用于获取版本的命令行参数
            force: 是否强制重新检测，忽略已存储的路径
            
        Returns:
            检测到的可执行文件路径，如果未找到则返回None
        """
        # 获取带扩展名的可执行文件名
        full_executable_name = self._get_executable_name(executable_name)
        
        # 检查是否已经存储了路径，且不强制重新检测
        if not force and executable_name in self.config:
            stored_path = self.config[executable_name]
            if os.path.exists(stored_path) and self._check_executable_version(stored_path, version_flags):
                return stored_path
        
        # 搜索常见路径
        paths_to_check = self._get_platform_paths()
        
        # 尝试直接执行，看是否在PATH中
        try:
            result = subprocess.run(
                [full_executable_name] + version_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 获取可执行文件的完整路径
                if platform.system() == 'Windows':
                    # Windows系统使用where命令
                    where_result = subprocess.run(
                        ['where', full_executable_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if where_result.returncode == 0:
                        # 根据text参数类型处理stdout
                        stdout = where_result.stdout
                        if isinstance(stdout, bytes):
                            stdout = stdout.decode('utf-8')
                        path = stdout.strip().split('\n')[0]
                        self.config[executable_name] = path
                        self._save_config()
                        return path
                else:
                    # Unix-like系统使用which命令
                    which_result = subprocess.run(
                        ['which', full_executable_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if which_result.returncode == 0:
                        # 根据text参数类型处理stdout
                        stdout = which_result.stdout
                        if isinstance(stdout, bytes):
                            stdout = stdout.decode('utf-8')
                        path = stdout.strip()
                        self.config[executable_name] = path
                        self._save_config()
                        return path
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            pass
        
        # 遍历所有可能的路径
        for path in paths_to_check:
            executable_path = os.path.join(path, full_executable_name)
            if os.path.exists(executable_path):
                if self._check_executable_version(executable_path, version_flags):
                    self.config[executable_name] = executable_path
                    self._save_config()
                    return executable_path
        
        # 未找到可执行文件
        return None
    
    def get_path(self, executable_name: str) -> Optional[str]:
        """
        获取可执行文件路径（不执行检测）
        
        Args:
            executable_name: 可执行文件名称
            
        Returns:
            存储的可执行文件路径，如果未存储则返回None
        """
        return self.config.get(executable_name)
    
    def set_path(self, executable_name: str, path: str) -> bool:
        """
        手动设置可执行文件路径
        
        Args:
            executable_name: 可执行文件名称
            path: 可执行文件路径
            
        Returns:
            设置成功返回True，否则返回False
        """
        if os.path.exists(path):
            self.config[executable_name] = path
            self._save_config()
            return True
        return False
    
    def clear_path(self, executable_name: str) -> None:
        """
        清除存储的可执行文件路径
        
        Args:
            executable_name: 可执行文件名称
        """
        if executable_name in self.config:
            del self.config[executable_name]
            self._save_config()
    
    def get_all_paths(self) -> Dict[str, str]:
        """
        获取所有存储的可执行文件路径
        
        Returns:
            所有存储的可执行文件路径字典
        """
        return self.config.copy()

# 全局检测器实例
global_detector = ExecutableDetector()

# 辅助函数
def detect_executable(executable_name: str, version_flags: List[str] = ['--version'], force: bool = False) -> Optional[str]:
    """
    检测可执行文件路径（全局函数）
    
    Args:
        executable_name: 可执行文件名称
        version_flags: 用于获取版本的命令行参数
        force: 是否强制重新检测
        
    Returns:
        检测到的可执行文件路径，如果未找到则返回None
    """
    return global_detector.detect(executable_name, version_flags, force)

def get_executable_path(executable_name: str) -> Optional[str]:
    """
    获取可执行文件路径（全局函数）
    
    Args:
        executable_name: 可执行文件名称
        
    Returns:
        存储的可执行文件路径，如果未存储则返回None
    """
    return global_detector.get_path(executable_name)

def set_executable_path(executable_name: str, path: str) -> bool:
    """
    手动设置可执行文件路径（全局函数）
    
    Args:
        executable_name: 可执行文件名称
        path: 可执行文件路径
        
    Returns:
        设置成功返回True，否则返回False
    """
    return global_detector.set_path(executable_name, path)

def clear_executable_path(executable_name: str) -> None:
    """
    清除存储的可执行文件路径（全局函数）
    
    Args:
        executable_name: 可执行文件名称
    """
    global_detector.clear_path(executable_name)

def get_all_executable_paths() -> Dict[str, str]:
    """
    获取所有存储的可执行文件路径（全局函数）
    
    Returns:
        所有存储的可执行文件路径字典
    """
    return global_detector.get_all_paths()

if __name__ == '__main__':
    """
    测试代码
    """
    # 测试检测wkhtmltopdf
    print("Testing wkhtmltopdf detection...")
    wkhtmltopdf_path = detect_executable('wkhtmltopdf')
    if wkhtmltopdf_path:
        print(f"Found wkhtmltopdf at: {wkhtmltopdf_path}")
    else:
        print("wkhtmltopdf not found")
    
    # 测试检测python
    print("\nTesting python detection...")
    python_path = detect_executable('python')
    if python_path:
        print(f"Found python at: {python_path}")
    else:
        print("python not found")
    
    # 打印所有存储的路径
    print("\nAll stored paths:")
    for name, path in get_all_executable_paths().items():
        print(f"  {name}: {path}")
